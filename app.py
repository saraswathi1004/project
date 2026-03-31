import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import os
from datetime import datetime
from streamlit_geolocation import streamlit_geolocation
from geopy.distance import geodesic
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP Configuration (configure these for your email server)
# For Gmail: Use your Gmail address as username and create an App Password in your Google Account
# Go to Google Account > Security > 2-Step Verification > App Passwords to create one
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "ttdreact@gmail.com"  # Your Gmail address
SMTP_PASSWORD = "vudtkrdxylxvvmhb"  # Replace with your 16-character App Password
ADMIN_EMAIL = "iamsarawathi12@gmail.com"  # Change to admin's email address

# Define valid areas
VALID_ADDRESSES = [
    "Avadi, Poonamallee, Thiruvallur, Tamil Nadu, 600054, India","CMWSSB Division 132, Ward 132, Zone 10 Kodambakkam, Chennai Corporation, Chennai, Tamil Nadu, 600026, India","Munusamy Salai, CMWSSB Division 128, Ward 128, Zone 10 Kodambakkam, Chennai Corporation, Chennai, Tamil Nadu, 600078, India","Loganatha Nagar Second Street, CMWSSB Division 108, Ward 108, Zone 8 Anna Nagar, Chennai Corporation, Chennai, Tamil Nadu, 600107, India"
]

# Geocode all valid addresses to get their coordinates
geolocator = Nominatim(user_agent="complaint_app")
VALID_LOCATIONS = []
for addr in VALID_ADDRESSES:
    try:
        location = geolocator.geocode(addr, timeout=10)
        if location:
            VALID_LOCATIONS.append((location.latitude, location.longitude, addr))
    except:
        pass

# Calculate center from all valid locations
if VALID_LOCATIONS:
    CENTER_LAT = sum(loc[0] for loc in VALID_LOCATIONS) / len(VALID_LOCATIONS)
    CENTER_LNG = sum(loc[1] for loc in VALID_LOCATIONS) / len(VALID_LOCATIONS)
else:
    CENTER_LAT, CENTER_LNG = None, None

# Function to send email notification to admin
def send_complaint_email(to_email, from_email, complaint_title, complaint_description, complaint_address, student_name, student_email):
    """Send email to admin when a new complaint is submitted"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{student_name} <{SMTP_USERNAME}>"
        msg['To'] = to_email
        msg['Subject'] = f"New Complaint Submitted: {complaint_title}"
        
        body = f"""
A new complaint has been submitted.

Student Details:
- Name: {student_name}
- Email: {student_email}

Complaint Details:
- Title: {complaint_title}
- Description: {complaint_description}
- Address: {complaint_address}

Please login to the admin panel to review and respond to this complaint.
"""
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError:
        st.error("Email authentication failed. Please check SMTP username and password.")
        return False
    except smtplib.SMTPException as e:
        st.error(f"SMTP Error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

st.set_page_config(page_title="Complaint Management System", layout="wide")

st.markdown("""
<style>
html, body {
    background: #000000;
    color: white;
}
.stTabs [data-baseweb="tab-list"] {
    background-color: rgba(255,255,255,0.1);
    border-radius: 10px;
}
.stTabs [data-baseweb="tab"] {
    color: white;
    font-weight: bold;
}
.stButton>button {
    background-color: #e74c3c;
    color: white;
    border-radius: 10px;
    border: none;
}
.stTextInput>div>div>input {
    border-radius: 10px;
    border: 2px solid #e74c3c;
    background-color: #34495e;
    color: white;
}
.stTextArea>div>textarea {
    border-radius: 10px;
    border: 2px solid #e74c3c;
    background-color: #34495e;
    color: white;
}
.stDataFrame {
    background-color: rgba(255,255,255,0.1);
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.image("https://via.placeholder.com/800x200/000000/FFFFFF?text=Geo+Tag+Complaint+Management+System", width=800)
st.title("St peter's college of engineering and technology")
st.title("College complaint management system")

# Load data
df = pd.DataFrame(columns=['id', 'title', 'description', 'address', 'lat', 'lng', 'timestamp', 'image_path', 'user_id', 'status', 'admin_reply'])
if os.path.exists('complaints.csv'):
    df = pd.read_csv('complaints.csv')
    # Convert all numeric columns safely
    numeric_cols = ['id', 'user_id', 'lat', 'lng']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    if 'image_path' not in df.columns:
        df['image_path'] = None
    if 'status' not in df.columns:
        df['status'] = 'pending'
    if 'admin_reply' not in df.columns:
        df['admin_reply'] = None
    df['admin_reply'] = df['admin_reply'].fillna('').astype(str)
    # Sort by id descending and reset index
    df = df.sort_values('id', ascending=False).reset_index(drop=True)

# Load users
users_df = pd.DataFrame(columns=['id', 'username', 'password', 'email', 'role', 'register_number', 'year_of_study', 'department', 'semester'])
if os.path.exists('users.csv'):
    users_df = pd.read_csv('users.csv')
    # Convert numeric columns safely
    numeric_cols_users = ['id', 'register_number']
    for col in numeric_cols_users:
        if col in users_df.columns:
            users_df[col] = pd.to_numeric(users_df[col], errors='coerce').fillna(0)
    # Add missing columns if they don't exist
    for col in ['register_number', 'year_of_study', 'department', 'semester']:
        if col not in users_df.columns:
            users_df[col] = ''
else:
    # Add default admin
    admin_row = {'id': 1, 'username': 'admin', 'password': 'admin123', 'email': 'admin@example.com', 'role': 'admin', 'register_number': '', 'year_of_study': '', 'department': '', 'semester': ''}
    users_df = pd.DataFrame([admin_row])
    users_df.to_csv('users.csv', index=False)

if 'user' not in st.session_state:
    st.header("🔐 Login / Register")
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
            if not user.empty:
                st.session_state['user'] = user.iloc[0].to_dict()
                st.success("Logged in!")
                st.balloons()
                st.rerun()
            else:
                st.error("Invalid credentials")
    with tab2:
        st.subheader("📝 Register New Account")
        reg_username = st.text_input("Username", key="reg_user")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_email = st.text_input("Email", key="reg_email")
        reg_register_number = st.number_input("Register Number", min_value=112700000000, max_value=112799999999, step=1, key="reg_reg_num")
        reg_year = st.selectbox("Year of Study", ["", "1st Year", "2nd Year", "3rd Year", "4th Year"], key="reg_year")
        reg_department = st.selectbox("Department", ["", "Computer Science Engineering", "Electrical Engineering", "Electronics Engineering", "Mechanical Engineering", "Civil Engineering", "Information Technology", "Artificial Intelligence & Data Science", "Other"], key="reg_dept")
        reg_semester = st.selectbox("Semester", ["", "1st Semester", "2nd Semester", "3rd Semester", "4th Semester", "5th Semester", "6th Semester", "7th Semester", "8th Semester"], key="reg_sem")
        if st.button("Register"):
            if reg_username and reg_password and reg_email and reg_register_number and reg_year and reg_department and reg_semester:
                # Validate register number - must start with 1127 and be exactly 12 digits
                reg_num_str = str(reg_register_number)
                if not reg_num_str.startswith('1127'):
                    st.error("Register Number must start with 1127")
                elif len(reg_num_str) != 12:
                    st.error("Register Number must be exactly 12 numbers")
                elif reg_username in users_df['username'].values:
                    st.error("Username exists")
                else:
                    new_user_id = len(users_df) + 1
                    new_user = {'id': new_user_id, 'username': reg_username, 'password': reg_password, 'email': reg_email, 'role': 'user', 'register_number': reg_num_str, 'year_of_study': reg_year, 'department': reg_department, 'semester': reg_semester}
                    users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
                    users_df.to_csv('users.csv', index=False)
                    st.success("Registered! Please login.")
                    st.balloons()
            else:
                st.error("Please fill all fields")
else:
    user = st.session_state['user']
    if st.sidebar.button("Logout"):
        del st.session_state['user']
        st.rerun()
    if user['role'] == 'admin':
        # Admin panel
        st.header("Admin Panel")
        tab1, tab2, tab3 = st.tabs(["👥 User Details", "📋 Complaint Details", "✅ Approve/Reply"])
        with tab1:
            st.subheader("👥 Registered Users")
            st.dataframe(users_df)
        with tab2:
            st.subheader("📋 All Complaints (Recent First)")
            df_display = df.sort_values('timestamp', ascending=False)
            if not df_display.empty:
                for idx, row in df_display.iterrows():
                    with st.expander(f"Complaint {row['id']}: {row['title']}"):
                        st.write(f"**Description:** {row['description']}")
                        st.write(f"**Address:** {row['address']}")
                        st.write(f"**Status:** {row['status']}")
                        st.write(f"**Time:** {row['timestamp']}")
                        if pd.notna(row['image_path']) and os.path.exists(row['image_path']):
                            st.image(row['image_path'], caption="Complaint Image", width=300)
                        else:
                            st.write("No image uploaded")
                        st.divider()
            else:
                st.write("No complaints yet.")
        with tab3:
            st.subheader("✅ Manage Complaints")
            for idx, row in df.iterrows():
                with st.expander(f"Complaint {row['id']}: {row['title']}"):
                    st.write(f"Description: {row['description']}")
                    st.write(f"Status: {row['status']}")
                    if pd.notna(row['image_path']) and os.path.exists(row['image_path']):
                        st.image(row['image_path'], caption="Complaint Image", width=300)
                    else:
                        st.write("No image uploaded")
                    if pd.notna(row['admin_reply']):
                        st.write(f"Reply: {row['admin_reply']}")
                    new_status = st.selectbox("Status", ["pending", "approved", "rejected"], index=["pending", "approved", "rejected"].index(row['status']), key=f"status_{row['id']}")
                    reply = st.text_area("Reply", value=row['admin_reply'] if pd.notna(row['admin_reply']) else "", key=f"reply_{row['id']}")
                    if st.button("Update", key=f"update_{row['id']}"):
                        df.at[idx, 'status'] = new_status
                        df.at[idx, 'admin_reply'] = reply
                        df.to_csv('complaints.csv', index=False)
                        st.success("Updated!")
                        st.balloons()
    else:
        # User panel
        st.header("User Panel")
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Complaint Form", "📋 My Complaints", "🗺️ Map View", "👤 Profile"])
        with tab1:
            st.subheader("📝 Submit Complaint")
            st.subheader("Valid Areas")
            for addr in VALID_ADDRESSES:
                st.write(f"- {addr}")
            title = st.text_input("Title")
            description = st.text_area("Description")
            use_current = st.checkbox("Use current location")
            if use_current:
                location_data = streamlit_geolocation()
                if location_data:
                    lat = location_data['latitude']
                    lng = location_data['longitude']
                    geolocator = Nominatim(user_agent="complaint_app")
                    location = geolocator.reverse((lat, lng))
                    address = location.address if location else "Current Location"
                    st.write(f"Detected Address: {address}")
                else:
                    st.error("Unable to get current location.")
                    lat, lng, address = None, None, None
            else:
                address = st.text_input("Address")
                if address:
                    geolocator = Nominatim(user_agent="complaint_app")
                    location = geolocator.geocode(address)
                    if location:
                        lat, lng = location.latitude, location.longitude
                    else:
                        st.error("Address not found.")
                        lat, lng = None, None
                else:
                    lat, lng = None, None
            image = st.camera_input("Capture Photo (optional)")
            if st.button("Submit Complaint"):
                if title and description and lat is not None and lng is not None:
                    # Validate location - check if within 5km of ANY valid location
                    if VALID_LOCATIONS:
                        is_valid = False
                        try:
                            lat_val = float(lat)
                            lng_val = float(lng)
                        except Exception:
                            st.error("Invalid latitude/longitude values. Please retry location detection.")
                            lat_val, lng_val = None, None

                        if lat_val is not None and lng_val is not None:
                            for valid_lat, valid_lng, valid_addr in VALID_LOCATIONS:
                                try:
                                    valid_lat_val = float(valid_lat)
                                    valid_lng_val = float(valid_lng)
                                    distance_val = geodesic((lat_val, lng_val), (valid_lat_val, valid_lng_val)).km
                                    distance_km = float(distance_val)
                                except Exception:
                                    continue

                                if distance_km <= 5:
                                    is_valid = True
                                    break

                        if not is_valid:
                            st.error("Complaint location is outside the valid area.")
                        else:
                            new_id = len(df) + 1
                            timestamp = datetime.now().isoformat()
                            if image:
                                os.makedirs('images', exist_ok=True)
                                filename = f"complaint_{new_id}.png"
                                with open(f"images/{filename}", "wb") as f:
                                    f.write(image.getvalue())
                                image_path = f"images/{filename}"
                            else:
                                image_path = None
                            new_row = {'id': new_id, 'title': title, 'description': description, 'address': address, 'lat': lat, 'lng': lng, 'timestamp': timestamp, 'image_path': image_path, 'user_id': user['id'], 'status': 'pending', 'admin_reply': None}
                            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                            df.to_csv('complaints.csv', index=False)
                            # Send email notification to admin
                            email_sent = send_complaint_email(
                                to_email=ADMIN_EMAIL,
                                from_email=SMTP_USERNAME,  # Use SMTP email as sender (required for most providers)
                                complaint_title=title,
                                complaint_description=description,
                                complaint_address=address,
                                student_name=user['username'],
                                student_email=user['email']
                            )
                            if email_sent:
                                st.success("Complaint submitted and email notification sent to admin!")
                            else:
                                st.success("Complaint submitted! (Email notification failed)")
                            st.balloons()
                else:
                    st.error("Please fill all fields and ensure location is set.")
        with tab2:
            st.subheader("My Complaints")
            user_complaints = df[df['user_id'] == user['id']]
            if not user_complaints.empty:
                for _, row in user_complaints.iterrows():
                    st.subheader(row['title'])
                    st.write(f"Description: {row['description']}")
                    st.write(f"Address: {row['address']}")
                    st.write(f"Status: {row['status']}")
                    if pd.notna(row['admin_reply']):
                        st.write(f"Admin Reply: {row['admin_reply']}")
                    st.write(f"Time: {row['timestamp']}")
                    if pd.notna(row['image_path']) and os.path.exists(row['image_path']):
                        st.image(row['image_path'])
                    st.divider()
            else:
                st.write("No complaints yet.")
        with tab3:
            st.subheader("Map View")
            user_complaints = df[df['user_id'] == user['id']]
            if not user_complaints.empty:
                m = folium.Map(location=[user_complaints['lat'].mean(), user_complaints['lng'].mean()], zoom_start=10)
                for _, row in user_complaints.iterrows():
                    folium.Marker([row['lat'], row['lng']], popup=row['title']).add_to(m)
                st_folium(m, width=700, height=500)
            else:
                st.write("No complaints to display on map.")
        with tab4:
            st.subheader("Profile")
            st.write(f"Username: {user['username']}")
            st.write(f"Email: {user['email']}")
            st.write(f"Role: {user['role']}")
            # Display additional user details if available
            user_details = users_df[users_df['id'] == user['id']]
            if not user_details.empty:
                reg_num = user_details.iloc[0]['register_number'] if 'register_number' in user_details.columns else 0
                st.write(f"Register Number: {int(reg_num) if pd.notna(reg_num) and reg_num != 0 else 'N/A'}")
                if 'year_of_study' in user_details.columns and user_details.iloc[0]['year_of_study']:
                    st.write(f"Year of Study: {user_details.iloc[0]['year_of_study']}")
                if 'department' in user_details.columns and user_details.iloc[0]['department']:
                    st.write(f"Department: {user_details.iloc[0]['department']}")
                if 'semester' in user_details.columns and user_details.iloc[0]['semester']:
                    st.write(f"Semester: {user_details.iloc[0]['semester']}")
            st.subheader("Current Location")
            if st.button("Get My Location"):
                location_data = streamlit_geolocation()
                if location_data:
                    lat = location_data['latitude']
                    lng = location_data['longitude']
                    st.write(f"Latitude: {lat}")
                    st.write(f"Longitude: {lng}")
                    geolocator = Nominatim(user_agent="complaint_app")
                    try:
                        location = geolocator.reverse((lat, lng), timeout=10)
                        address = location.address if location else "Unable to determine address"
                    except:
                        address = "Unable to determine address"
                    st.write(f"Address: {address}")
                else:
                    st.error("Unable to retrieve location. Please ensure location permissions are granted.")
