import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import sqlite3
from utils.image_processing import process_image, blur_faces, remove_metadata
from utils.ocr import extract_vin
from utils.stolen_vehicle_api import check_stolen_status
from utils.bait_car_api import get_nearby_bait_cars
from utils.redis_manager import RedisManager
from database.models import create_tables, save_report, delete_old_reports
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, DEBUG_MODE

app = Flask(__name__)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
redis_manager = RedisManager()

# Ensure database tables exist
create_tables()


@app.route('/')
def index():
    """Home page route"""
    return """
    <html>
    <head>
        <title>Indianapolis Public Safety Bot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #003366; }
            .commands { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Indianapolis Public Safety SMS Chatbot</h1>
        <p>This is the server for the Indianapolis Public Safety SMS Chatbot. Text one of the following commands to the Twilio phone number:</p>
        
        <div class="commands">
            <p><strong>report [details]</strong> + photo: Report suspicious activity</p>
            <p><strong>check vin</strong> + photo: Check if a vehicle is stolen</p>
            <p><strong>bait cars</strong>: Check for nearby bait cars</p>
            <p><strong>RED</strong>: Emergency help (triggers call)</p>
            <p><strong>call mom</strong>: Fake family emergency call</p>
        </div>
        
        <p>Server status: <span style="color: green; font-weight: bold;">ONLINE</span></p>
    </body>
    </html>
    """
    
    
@app.route('/sms', methods=['POST'])
def sms_reply():
    """Main route for handling incoming SMS messages"""
    
    # Get incoming message details
    incoming_msg = request.values.get('Body', '').strip().lower()
    media_count = int(request.values.get('NumMedia', 0))
    from_number = request.values.get('From', '')
    latitude = request.values.get('Latitude')
    longitude = request.values.get('Longitude')
    
    # Initialize Twilio response
    resp = MessagingResponse()
    
    # Process emergency keywords (priority check)
    if "red" in incoming_msg.lower():
        # Trigger emergency call
        client.calls.create(
            to=from_number,
            from_=TWILIO_PHONE_NUMBER,
            url=request.url_root + 'emergency_call'
        )
        resp.message("Initiating emergency call to your phone. Stay safe.")
        return str(resp)
    
    elif "call mom" in incoming_msg.lower():
        # Trigger family emergency call
        client.calls.create(
            to=from_number,
            from_=TWILIO_PHONE_NUMBER,
            url=request.url_root + 'family_call'
        )
        resp.message("Initiating family emergency call to your phone.")
        return str(resp)
    
    # Process based on message content
    if "report" in incoming_msg and media_count > 0:
        # Crime reporting with image
        report_text = incoming_msg.replace("report", "").strip()
        
        # Process attached media
        media_urls = []
        for i in range(media_count):
            media_url = request.values.get(f'MediaUrl{i}')
            media_type = request.values.get(f'MediaContentType{i}')
            
            if media_type.startswith('image/'):
                # Process image - remove metadata and blur faces
                processed_img_path = process_image(media_url)
                # Save to database with report
                media_urls.append(processed_img_path)
        
        # Save report to database (anonymously)
        report_id = save_report(report_text, media_urls, latitude, longitude)
        resp.message(f"Thank you for your report. Your anonymous report ID is {report_id}. All images have been processed to protect privacy. The report will be automatically deleted after 48 hours.")
    
    elif "check vin" in incoming_msg and media_count > 0:
        # Stolen vehicle check
        for i in range(media_count):
            media_url = request.values.get(f'MediaUrl{i}')
            media_type = request.values.get(f'MediaContentType{i}')
            
            if media_type.startswith('image/'):
                # Extract VIN using OCR
                vin = extract_vin(media_url)
                if vin:
                    # Check if vehicle is stolen
                    stolen_status = check_stolen_status(vin)
                    if stolen_status['is_stolen']:
                        resp.message(f"⚠️ ALERT: This vehicle with VIN {vin} is REPORTED STOLEN. Do not approach. Contact IMPD at 317-327-3811.")
                    else:
                        resp.message(f"✅ Vehicle with VIN {vin} is not reported stolen in our database.")
                else:
                    resp.message("Could not detect a VIN in the image. Please try with a clearer photo of the VIN plate.")
                break
        else:
            resp.message("Please send a photo of the vehicle's VIN plate for checking.")
    
    elif "bait cars" in incoming_msg:
        # Bait car alerts check
        if latitude and longitude:
            nearby_bait_cars = get_nearby_bait_cars(float(latitude), float(longitude))
            if nearby_bait_cars:
                resp.message("🚨 Police bait car active near you. Park here to deter theft!")
            else:
                resp.message("No active bait cars currently reported in your immediate area.")
        else:
            resp.message("Location information is needed to check for nearby bait cars. Please enable location sharing.")
    
    else:
        # Help message for unknown commands
        resp.message("Indianapolis Public Safety Bot Commands:\n"
                     "- 'report [details]' + photo: Report suspicious activity\n"
                     "- 'check vin' + photo: Check if a vehicle is stolen\n"
                     "- 'bait cars': Check for nearby bait cars\n"
                     "- 'RED': Emergency help (triggers call)\n"
                     "- 'call mom': Fake family emergency call")
    
    return str(resp)

@app.route('/emergency_call', methods=['POST'])
def emergency_call():
    """Route for emergency call TwiML"""
    response = VoiceResponse()
    response.play(url=request.url_root + 'static/audio/emergency_call.mp3')
    response.say("This is an emergency call. If you're in danger, please try to get to safety. "
                 "Police have been notified of your location and are on their way. "
                 "Stay on the line if possible.", voice='woman')
    response.pause(length=30)
    response.say("Help is on the way. Please stay calm.", voice='woman')
    return Response(str(response), mimetype='text/xml')

@app.route('/family_call', methods=['POST'])
def family_call():
    """Route for fake family emergency call TwiML"""
    response = VoiceResponse()
    response.play(url=request.url_root + 'static/audio/family_call.mp3')
    response.say("Hey, it's mom. There's an emergency at home. "
                 "We need you to come right away. The situation is urgent. "
                 "Please call me back as soon as you can.", voice='woman')
    response.pause(length=5)
    response.say("I hope you can get home soon. It's important.", voice='woman')
    return Response(str(response), mimetype='text/xml')

@app.route('/cleanup', methods=['GET'])
def cleanup_old_reports():
    """Admin route to manually trigger cleanup of old reports"""
    if request.args.get('key') == os.environ.get('ADMIN_KEY'):
        count = delete_old_reports()
        return f"Deleted {count} reports older than 48 hours."
    return "Unauthorized", 401

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE)