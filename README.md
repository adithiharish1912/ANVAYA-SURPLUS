
# Anvaya | AI Food Waste Management and Redistribution System

## About the Project

Anvaya is a web-based food waste management and redistribution system designed to reduce food waste by connecting food donors with NGOs and organizations that serve people in need.

The platform allows donors to submit surplus food donations, administrators to review and approve donations, and NGOs to request food pickups. The system also displays impact statistics to track food redistribution.

## Objectives

- Reduce food wastage.
- Connect food donors with NGOs.
- Simplify food donation and pickup management.
- Provide an admin dashboard for donation approval.
- Track the quantity of food donated and collected.
- Encourage sustainable food redistribution.

## Main Features

### 1. Donor Portal
- Submit surplus food donations.
- Enter food quantity, location, contact details, and safe-until date.
- Track the overall impact of approved donations.

### 2. Admin Portal
- Secure admin login.
- View submitted donations.
- Approve or reject donations.
- View donation statistics.
- Mark approved donations as collected after an NGO requests pickup.

### 3. NGO Portal
- View approved food donations.
- Check food details and pickup locations.
- Submit pickup requests with NGO contact information.

### 4. Impact Dashboard
- Display the number of approved donations.
- Display the total quantity of approved food.
- Display the quantity of food collected.

## Technologies Used

- Frontend: HTML, CSS, JavaScript
- Backend: Python and Flask
- Database: SQLite
- Development Environment: Visual Studio Code

## Project Structure

```text
ANVAYA1/
├── app.py
├── anvaya.db
├── requirements.txt
├── README.md
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    ├── base.html
    ├── index.html
    ├── admin_login.html
    ├── admin_dashboard.html
    └── ngo_dashboard.html
```

Note: `anvaya.db` is created automatically when the application initializes. It may not appear until the application is run.

## Installation and Setup

### Prerequisites
- Python 3
- Visual Studio Code
- Internet connection for installing Flask

### Step 1: Open the project
Open the ANVAYA1 folder in Visual Studio Code.

### Step 2: Install dependencies
Open the terminal and run:

```bash
python3 -m pip install -r requirements.txt
```

### Step 3: Run the application

```bash
python3 app.py
```

### Step 4: Open the website

Open the following URL in your browser:

http://127.0.0.1:5000/

## Application Portals

- Donor Portal: http://127.0.0.1:5000/
- Admin Portal: http://127.0.0.1:5000/admin/login
- NGO Portal: http://127.0.0.1:5000/ngo
- Impact API: http://127.0.0.1:5000/api/impact

## Demo Admin Credentials

Username: admin

Password: AnvayaDemo123!

These are development credentials only. Change them before public deployment.

## Future Enhancements

- AI-based food demand prediction.
- NGO registration and login.
- Donor and NGO profile management.
- Automated food expiry alerts.
- Volunteer management and pickup tracking.
- Location-based donor and NGO matching.
- Email or SMS notifications.
- Advanced analytics and reporting.
- Deployment with a production database and secure authentication.

## Project Scope and Limitations

This is an educational mini-project prototype. The current version supports basic donation submission, admin approval, NGO pickup requests, and impact statistics.

AI-based prediction, automated notifications, and separate NGO authentication are planned enhancements and are not yet implemented.

## Conclusion

Anvaya aims to make food redistribution more organized and accessible by connecting surplus food donors with NGOs. By improving donation coordination and tracking, the project supports food waste reduction and more responsible resource utilization.

---

Developed as a mini-project on AI Food Waste Management and Redistribution.
