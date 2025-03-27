# SwiftVerify - Polling Station Voter Verification System

## Overview

SwiftVerify is a web application designed to streamline the voter verification process at polling stations. By leveraging Flask for the backend and incorporating both automated data matching and biometric verification, SwiftVerify aims to significantly reduce waiting times and enhance the integrity of the electoral process.

## Features

* **Automated Data Matching:**
    * Utilizes voter ID details to quickly retrieve and verify voter information from database.
    * Reduces manual data entry and minimizes the risk of human error.
* **Biometric Verification:**
    * Integrates fingerprint to ensure the identity of the voter.
    * Adds an extra layer of security, preventing fraudulent voting and enhancing the accuracy of the verification process.
* **Flask Backend:**
    * Built using the Python Flask framework, providing a robust and scalable backend for handling data processing.
    * Makes use of SQLITE3 library database to store voter information.
* **User-Friendly Interface:**
    * Intuitive web interface designed for ease of use by polling station staff.
    * Provides clear and concise feedback on the verification process.
* **Reporting and Logging:**
    * Logs all verification attempts for audit and accountability purposes.

## Technologies Used

* **Backend:** Python (Flask)
* **Database:** SQLite
* **Biometric Verification:** fingerprint scanner
* **Frontend:** HTML, CSS
* **API:** RESTful APIs for data exchange.

## Installation and Setup

1.  **Install dependencies:**
    ```bash
    pip install flask sqlite3
    ```
2.  **Configure the database:**
    * It will automatically create a database named voter_data.db
3.  **Access the application:**
    * Open a web browser and navigate to `http://127.0.0.1:5000/` or the specified address.
  
* **Login Credentials:**
    * Officer 1: `officer1`, Passcode: `password123`
    * Officer 2: `officer2`, Passcode: `password123`
* **Test Aadhar IDs:**
    * 123456789012
    * 987654321098
    * 488621545365
    * 432654567895



      **Made With Love by Code Catalysts Team**
