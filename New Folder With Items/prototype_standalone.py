#!/usr/bin/env python
"""
Pattern Overview Prototype - STANDALONE VERSION (No Django)
Test concept for 12-week horizontal scrolling view with pure mock data

Usage:
    python prototype_standalone.py
    Then visit: http://127.0.0.1:5000/
"""

from datetime import datetime, timedelta
from flask import Flask, render_template_string

app = Flask(__name__)

# Mock data generation
def generate_mock_data(weeks=12, start_date=None):
    """Generate mock shift pattern data for testing
    
    Args:
        weeks: Number of weeks to generate (default 12)
        start_date: Optional start date. If None, uses current week's Sunday (rolling window)
    """
    
    # Bramley Unit - Real Staff Data
    # SSCW Day (3) + SSCWN Night (3) + Day Staff (9 staff) + Night Staff (9 staff) = 24 total
    staff_list = [
        # === DAY SSCW MANAGERS - Team A (3 SSCW) ===
        {'sap': '000707', 'first_name': 'Morag', 'last_name': 'Henderson', 'role': 'SSCW', 'unit': 'Bramley', 'contracted_hours': 37.5},  # Team A
        {'sap': '000723', 'first_name': 'Sarah', 'last_name': 'Mitchell', 'role': 'SSCW', 'unit': 'Cherry', 'contracted_hours': 37.5},  # Team A
        {'sap': '000730', 'first_name': 'Emma', 'last_name': 'Taylor', 'role': 'SSCW', 'unit': 'Grape', 'contracted_hours': 37.5},  # Team A
        # === DAY SSCW MANAGERS - Team B (3 SSCW) ===
        {'sap': '000708', 'first_name': 'Diane', 'last_name': 'Smith', 'role': 'SSCW', 'unit': 'Orange', 'contracted_hours': 37.5},  # Team B
        {'sap': '000724', 'first_name': 'Linda', 'last_name': 'Clarke', 'role': 'SSCW', 'unit': 'Pear', 'contracted_hours': 37.5},  # Team B
        {'sap': '000731', 'first_name': 'Rachel', 'last_name': 'Brown', 'role': 'SSCW', 'unit': 'Plum', 'contracted_hours': 37.5},  # Team B
        # === DAY SSCW MANAGERS - Team C (3 SSCW) ===
        {'sap': '000706', 'first_name': 'Jack', 'last_name': 'Barnes', 'role': 'SSCW', 'unit': 'Peach', 'contracted_hours': 37.5},  # Team C
        {'sap': '000725', 'first_name': 'Margaret', 'last_name': 'Wilson', 'role': 'SSCW', 'unit': 'Strawberry', 'contracted_hours': 37.5},  # Team C
        {'sap': '000732', 'first_name': 'Helen', 'last_name': 'Davis', 'role': 'SSCW', 'unit': 'Bramley', 'contracted_hours': 37.5},  # Team C
        # === NIGHT SSCWN MANAGERS - Team A (3 SSCWN) ===
        {'sap': '000710', 'first_name': 'Elaine', 'last_name': 'Martinez', 'role': 'SSCWN', 'unit': 'Bramley', 'contracted_hours': 37.5},  # Team A (last digit 0)
        {'sap': '000711', 'first_name': 'Patricia', 'last_name': 'Roberts', 'role': 'SSCWN', 'unit': 'Cherry', 'contracted_hours': 37.5},  # Team A (last digit 1)
        {'sap': '000712', 'first_name': 'Jennifer', 'last_name': 'Moore', 'role': 'SSCWN', 'unit': 'Grape', 'contracted_hours': 37.5},  # Team A (last digit 2)
        # === NIGHT SSCWN MANAGERS - Team B (3 SSCWN) ===
        {'sap': '000713', 'first_name': 'Wendy', 'last_name': 'Campbell', 'role': 'SSCWN', 'unit': 'Orange', 'contracted_hours': 37.5},  # Team B (last digit 3)
        {'sap': '000714', 'first_name': 'Barbara', 'last_name': 'White', 'role': 'SSCWN', 'unit': 'Pear', 'contracted_hours': 37.5},  # Team B (last digit 4)
        {'sap': '000715', 'first_name': 'Susan', 'last_name': 'Anderson', 'role': 'SSCWN', 'unit': 'Plum', 'contracted_hours': 37.5},  # Team B (last digit 5)
        # === NIGHT SSCWN MANAGERS - Team C (2 SSCWN) ===
        {'sap': '000716', 'first_name': 'John', 'last_name': 'Dollan', 'role': 'SSCWN', 'unit': 'Peach', 'contracted_hours': 37.5},  # Team C (last digit 6)
        {'sap': '000717', 'first_name': 'Dorothy', 'last_name': 'Green', 'role': 'SSCWN', 'unit': 'Strawberry', 'contracted_hours': 37.5},  # Team C (last digit 7)
        # === DAY STAFF (9) ===
        # Team A (3 staff) - 7 shifts/week
        {'sap': '000687', 'first_name': 'Ella', 'last_name': 'Ward', 'role': 'SCW', 'unit': 'Bramley', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000581', 'first_name': 'Megan', 'last_name': 'Howard', 'role': 'SCA', 'unit': 'Bramley', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000588', 'first_name': 'Victor', 'last_name': 'Watson', 'role': 'SCA', 'unit': 'Bramley', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team B (3 staff) - 7 shifts/week
        {'sap': '000667', 'first_name': 'Emily', 'last_name': 'Jones', 'role': 'SCW', 'unit': 'Bramley', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000557', 'first_name': 'Wendy', 'last_name': 'Thompson', 'role': 'SCA', 'unit': 'Bramley', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000548', 'first_name': 'Noah', 'last_name': 'Wilson', 'role': 'SCA', 'unit': 'Bramley', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team C (3 staff) - 8 shifts/week
        {'sap': '000673', 'first_name': 'Aaron', 'last_name': 'Clark', 'role': 'SCW', 'unit': 'Bramley', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000569', 'first_name': 'Sophia', 'last_name': 'Hall', 'role': 'SCA', 'unit': 'Bramley', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000560', 'first_name': 'Isaac', 'last_name': 'Wright', 'role': 'SCA', 'unit': 'Bramley', 'contracted_hours': 22.5},  # 3 shifts/week
        # === NIGHT STAFF (9) ===
        # Team A (3 staff) - 7 shifts/week
        {'sap': '000615', 'first_name': 'Daniel', 'last_name': 'Cohen', 'role': 'SCAN', 'unit': 'Bramley', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000600', 'first_name': 'Noah', 'last_name': 'Coleman', 'role': 'SCAN', 'unit': 'Bramley', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000611', 'first_name': 'Aaron', 'last_name': 'Cook', 'role': 'SCAN', 'unit': 'Bramley', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team B (3 staff) - 8 shifts/week
        {'sap': '000694', 'first_name': 'Blessing', 'last_name': 'Oghoa', 'role': 'SCWN', 'unit': 'Bramley', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000619', 'first_name': 'Caleb', 'last_name': 'King', 'role': 'SCAN', 'unit': 'Bramley', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000630', 'first_name': 'Oscar', 'last_name': 'Wright', 'role': 'SCAN', 'unit': 'Bramley', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team C (3 staff) - 7 shifts/week
        {'sap': '000700', 'first_name': 'Jacob', 'last_name': 'Campbell', 'role': 'SCWN', 'unit': 'Bramley', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000655', 'first_name': 'Emily', 'last_name': 'Rogers', 'role': 'SCAN', 'unit': 'Bramley', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000646', 'first_name': 'Taylor', 'last_name': 'Swifty', 'role': 'SCAN', 'unit': 'Bramley', 'contracted_hours': 22.5},  # 3 shifts/week
        
        # === CHERRY UNIT - Real Staff Data ===
        # Day Staff (9) + Night Staff (11) = 20 total
        # === DAY STAFF (9) ===
        # Team A (3 staff) - 7 shifts/week
        {'sap': '000688', 'first_name': 'Finn', 'last_name': 'Gray', 'role': 'SCW', 'unit': 'Cherry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000589', 'first_name': 'Zoe', 'last_name': 'Brooks', 'role': 'SCA', 'unit': 'Cherry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000582', 'first_name': 'Nathan', 'last_name': 'Peterson', 'role': 'SCA', 'unit': 'Cherry', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team B (3 staff) - 7 shifts/week
        {'sap': '000668', 'first_name': 'Frank', 'last_name': 'Garcia', 'role': 'SCW', 'unit': 'Cherry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000549', 'first_name': 'Olivia', 'last_name': 'Anderson', 'role': 'SCA', 'unit': 'Cherry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000558', 'first_name': 'Xander', 'last_name': 'White', 'role': 'SCA', 'unit': 'Cherry', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team C (3 staff) - 8 shifts/week
        {'sap': '000674', 'first_name': 'Bella', 'last_name': 'Ramirezz', 'role': 'SCW', 'unit': 'Cherry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000570', 'first_name': 'Tyler', 'last_name': 'Rivera', 'role': 'SCA', 'unit': 'Cherry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000561', 'first_name': 'Julia', 'last_name': 'Scott', 'role': 'SCA', 'unit': 'Cherry', 'contracted_hours': 22.5},  # 3 shifts/week
        
        # === NIGHT STAFF (11) ===
        # Team A (3 staff) - 7 shifts/week
        {'sap': '000616', 'first_name': 'Ella', 'last_name': 'Fitzgerald', 'role': 'SCAN', 'unit': 'Cherry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000601', 'first_name': 'Sam', 'last_name': 'Foster', 'role': 'SCAN', 'unit': 'Cherry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000612', 'first_name': 'Bella', 'last_name': 'Price', 'role': 'SCAN', 'unit': 'Cherry', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team B (3 staff) - 8 shifts/week
        {'sap': '000695', 'first_name': 'Peace', 'last_name': 'Sibbald', 'role': 'SCWN', 'unit': 'Cherry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000620', 'first_name': 'Diana', 'last_name': 'Doors', 'role': 'SCAN', 'unit': 'Cherry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000631', 'first_name': 'Piper', 'last_name': 'Scott', 'role': 'SCAN', 'unit': 'Cherry', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team C (5 staff) - 12 shifts/week
        {'sap': '000701', 'first_name': 'Katie', 'last_name': 'Mitchell', 'role': 'SCWN', 'unit': 'Cherry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000656', 'first_name': 'Frank', 'last_name': 'Cox', 'role': 'SCAN', 'unit': 'Cherry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000647', 'first_name': 'Janice', 'last_name': 'Evans', 'role': 'SCAN', 'unit': 'Cherry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000653', 'first_name': 'Abby', 'last_name': 'Rhodes', 'role': 'SCAN', 'unit': 'Cherry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000662', 'first_name': 'Precious', 'last_name': 'Richards', 'role': 'SCAN', 'unit': 'Cherry', 'contracted_hours': 15.0},  # 2 shifts/week
        
        # === GRAPE UNIT - Real Staff Data ===
        # Day Staff (10) + Night Staff (11) = 21 total
        # === DAY STAFF (10) ===
        # Team A (3 staff) - 7 shifts/week
        {'sap': '000684', 'first_name': 'Ben', 'last_name': 'Morris', 'role': 'SCW', 'unit': 'Grape', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000578', 'first_name': 'Jacob', 'last_name': 'Bailey', 'role': 'SCA', 'unit': 'Grape', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000593', 'first_name': 'Abby', 'last_name': 'Johnson', 'role': 'SCA', 'unit': 'Grape', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team B (3 staff) - 8 shifts/week
        {'sap': '000664', 'first_name': 'Bob', 'last_name': 'Johnson', 'role': 'SCW', 'unit': 'Grape', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000545', 'first_name': 'Karen', 'last_name': 'Hernandez', 'role': 'SCA', 'unit': 'Grape', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000554', 'first_name': 'Tina', 'last_name': 'Martin', 'role': 'SCA', 'unit': 'Grape', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team C (4 staff) - 10 shifts/week
        {'sap': '000678', 'first_name': 'Fiona', 'last_name': 'Young', 'role': 'SCW', 'unit': 'Grape', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000565', 'first_name': 'Nora', 'last_name': 'Green', 'role': 'SCA', 'unit': 'Grape', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000574', 'first_name': 'Wyatt', 'last_name': 'Roberts', 'role': 'SCA', 'unit': 'Grape', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000586', 'first_name': 'Sebastian', 'last_name': 'Ross', 'role': 'SCA', 'unit': 'Grape', 'contracted_hours': 22.5},  # 3 shifts/week
        
        # === NIGHT STAFF (11) ===
        # Team A (4 staff) - 11 shifts/week
        {'sap': '000691', 'first_name': 'Karen', 'last_name': 'Watson', 'role': 'SCWN', 'unit': 'Grape', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000605', 'first_name': 'Nora', 'last_name': 'Howard', 'role': 'SCAN', 'unit': 'Grape', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000597', 'first_name': 'Peter', 'last_name': 'Johnson', 'role': 'SCAN', 'unit': 'Grape', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000608', 'first_name': 'Xander', 'last_name': 'Ross', 'role': 'SCAN', 'unit': 'Grape', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team B (4 staff) - 10 shifts/week
        {'sap': '000624', 'first_name': 'Hannah', 'last_name': 'Barbera', 'role': 'SCAN', 'unit': 'Grape', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000639', 'first_name': 'Wyatt', 'last_name': 'Earp', 'role': 'SCAN', 'unit': 'Grape', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000635', 'first_name': 'Tyler', 'last_name': 'Green', 'role': 'SCAN', 'unit': 'Grape', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000628', 'first_name': 'Kyle', 'last_name': 'Young', 'role': 'SCAN', 'unit': 'Grape', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team C (3 staff) - 7 shifts/week
        {'sap': '000703', 'first_name': 'Megan', 'last_name': 'Roberts', 'role': 'SCWN', 'unit': 'Grape', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000660', 'first_name': 'Angela', 'last_name': 'Ripton', 'role': 'SCAN', 'unit': 'Grape', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000643', 'first_name': 'Quentin', 'last_name': 'Tarant', 'role': 'SCAN', 'unit': 'Grape', 'contracted_hours': 22.5},  # 3 shifts/week
        
        # === MANAGEMENT STAFF (Supernumerary) - 3 staff ===
        # Office Managers (2) - 5 shifts/week each
        {'sap': '001351', 'first_name': 'Thomas', 'last_name': 'Anderson', 'role': 'OM', 'unit': 'Management', 'contracted_hours': 37.5},  # 5 shifts/week
        {'sap': '001352', 'first_name': 'Sarah', 'last_name': 'Connor', 'role': 'OM', 'unit': 'Management', 'contracted_hours': 37.5},  # 5 shifts/week
        # Service Manager (1) - 5 shifts/week
        {'sap': '000704', 'first_name': 'Les', 'last_name': 'Dorson', 'role': 'SM', 'unit': 'Management', 'contracted_hours': 37.5},  # 5 shifts/week
        
        # === ORANGE UNIT - Real Staff Data ===
        # Day Staff (9) + Night Staff (8) = 17 total
        # === DAY STAFF (9) ===
        # Team A (3 staff) - 7 shifts/week
        {'sap': '000686', 'first_name': 'Daniel', 'last_name': 'Cox', 'role': 'SCW', 'unit': 'Orange', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000595', 'first_name': 'Janice', 'last_name': 'Henderson', 'role': 'SCA', 'unit': 'Orange', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000580', 'first_name': 'Leo', 'last_name': 'Kelly', 'role': 'SCA', 'unit': 'Orange', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team B (3 staff) - 7 shifts/week
        {'sap': '000666', 'first_name': 'David', 'last_name': 'Brown', 'role': 'SCW', 'unit': 'Orange', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000547', 'first_name': 'Mia', 'last_name': 'Gonzalez', 'role': 'SCA', 'unit': 'Orange', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000556', 'first_name': 'Victor', 'last_name': 'Perez', 'role': 'SCA', 'unit': 'Orange', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team C (3 staff) - 8 shifts/week
        {'sap': '000680', 'first_name': 'Hannah', 'last_name': 'King', 'role': 'SCW', 'unit': 'Orange', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000672', 'first_name': 'Zoe', 'last_name': 'Sanchez', 'role': 'SCW', 'unit': 'Orange', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000568', 'first_name': 'Ryan', 'last_name': 'Nelson', 'role': 'SCA', 'unit': 'Orange', 'contracted_hours': 22.5},  # 3 shifts/week
        
        # === NIGHT STAFF (8) ===
        # Team A (3 staff) - 7 shifts/week
        {'sap': '000693', 'first_name': 'Mia', 'last_name': 'Bryant', 'role': 'SCWN', 'unit': 'Orange', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000599', 'first_name': 'Rachel', 'last_name': 'Griffin', 'role': 'SCAN', 'unit': 'Orange', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000610', 'first_name': 'Zoe', 'last_name': 'Peterson', 'role': 'SCAN', 'unit': 'Orange', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team B (2 staff) - 5 shifts/week
        {'sap': '000637', 'first_name': 'Vincent', 'last_name': 'Baker', 'role': 'SCAN', 'unit': 'Orange', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000626', 'first_name': 'Isaac', 'last_name': 'Robinson', 'role': 'SCAN', 'unit': 'Orange', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team C (3 staff) - 8 shifts/week
        {'sap': '000699', 'first_name': 'Isabel', 'last_name': 'Rivera', 'role': 'SCWN', 'unit': 'Orange', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000645', 'first_name': 'Sebastian', 'last_name': 'Coen', 'role': 'SCAN', 'unit': 'Orange', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000654', 'first_name': 'David', 'last_name': 'Morris', 'role': 'SCAN', 'unit': 'Orange', 'contracted_hours': 15.0},  # 2 shifts/week
        
        # === PEACH UNIT - Real Staff Data ===
        # Day Staff (10) + Night Staff (9) = 19 total
        # === DAY STAFF (10) ===
        # Team A (4 staff) - 11 shifts/week
        {'sap': '000682', 'first_name': 'Zachary', 'last_name': 'Turner', 'role': 'SCW', 'unit': 'Peach', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000576', 'first_name': 'Harry', 'last_name': 'Coleman', 'role': 'SCA', 'unit': 'Peach', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000591', 'first_name': 'Beth', 'last_name': 'Griffin', 'role': 'SCA', 'unit': 'Peach', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000584', 'first_name': 'Quentin', 'last_name': 'Price', 'role': 'SCA', 'unit': 'Peach', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team B (3 staff) - 7 shifts/week
        {'sap': '000670', 'first_name': 'Henry', 'last_name': 'Davis', 'role': 'SCW', 'unit': 'Peach', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000553', 'first_name': 'Sam', 'last_name': 'Jackson', 'role': 'SCA', 'unit': 'Peach', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000551', 'first_name': 'Quinn', 'last_name': 'Taylor', 'role': 'SCA', 'unit': 'Peach', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team C (3 staff) - 7 shifts/week
        {'sap': '000676', 'first_name': 'Diana', 'last_name': 'Robinson', 'role': 'SCW', 'unit': 'Peach', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000572', 'first_name': 'Vincent', 'last_name': 'Mitchell', 'role': 'SCA', 'unit': 'Peach', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000563', 'first_name': 'Luna', 'last_name': 'Nguyen', 'role': 'SCA', 'unit': 'Peach', 'contracted_hours': 22.5},  # 3 shifts/week
        
        # === NIGHT STAFF (9) ===
        # Team A (3 staff) - 7 shifts/week
        {'sap': '000618', 'first_name': 'Gemma', 'last_name': 'Arthur', 'role': 'SCAN', 'unit': 'Peach', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000614', 'first_name': 'Chloe', 'last_name': 'Earlie', 'role': 'SCAN', 'unit': 'Peach', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000603', 'first_name': 'Uma', 'last_name': 'Reed', 'role': 'SCAN', 'unit': 'Peach', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team B (3 staff) - 7 shifts/week
        {'sap': '000697', 'first_name': 'Pedro', 'last_name': 'Wallace', 'role': 'SCWN', 'unit': 'Peach', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000622', 'first_name': 'Fiona', 'last_name': 'Bruce', 'role': 'SCAN', 'unit': 'Peach', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000633', 'first_name': 'Nathan', 'last_name': 'Nguyen', 'role': 'SCAN', 'unit': 'Peach', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team C (3 staff) - 8 shifts/week
        {'sap': '000651', 'first_name': 'Beth', 'last_name': 'Aimes', 'role': 'SCAN', 'unit': 'Peach', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000649', 'first_name': 'Zoe', 'last_name': 'Cooper', 'role': 'SCAN', 'unit': 'Peach', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000658', 'first_name': 'Henry', 'last_name': 'Gray', 'role': 'SCAN', 'unit': 'Peach', 'contracted_hours': 15.0},  # 2 shifts/week
        
        # === PEAR UNIT - Real Staff Data ===
        # SSCW Managers (2) + Day Staff (11) + Night Staff (12) = 25 total
        # === SSCW MANAGERS (2) ===
        {'sap': '000705', 'first_name': 'Joe', 'last_name': 'Brogan', 'role': 'SSCW', 'unit': 'Pear', 'contracted_hours': 37.5},  # Day SSCW Manager
        {'sap': '000714', 'first_name': 'Ian', 'last_name': 'Brown', 'role': 'SSCWN', 'unit': 'Pear', 'contracted_hours': 37.5},  # Night SSCW Manager
        # === DAY STAFF (11) ===
        # Team A (4 staff) - 11 shifts/week
        {'sap': '000683', 'first_name': 'Abigail', 'last_name': 'Cooper', 'role': 'SCW', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000585', 'first_name': 'Ruby', 'last_name': 'Barnes', 'role': 'SCA', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000577', 'first_name': 'Isabel', 'last_name': 'Foster', 'role': 'SCA', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000592', 'first_name': 'Natasha', 'last_name': 'Jones', 'role': 'SCA', 'unit': 'Pear', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team B (4 staff) - 11 shifts/week
        {'sap': '000671', 'first_name': 'Ivy', 'last_name': 'Rodriguez', 'role': 'SCW', 'unit': 'Pear', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000663', 'first_name': 'Alice', 'last_name': 'Smith', 'role': 'SCW', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000544', 'first_name': 'Jack', 'last_name': 'Martinez', 'role': 'SCA', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000552', 'first_name': 'Rachel', 'last_name': 'Moore', 'role': 'SCA', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team C (3 staff) - 7 shifts/week
        {'sap': '000677', 'first_name': 'Ethan', 'last_name': 'Walker', 'role': 'SCW', 'unit': 'Pear', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000573', 'first_name': 'Willow', 'last_name': 'Carter', 'role': 'SCA', 'unit': 'Pear', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000564', 'first_name': 'Mark', 'last_name': 'Hill', 'role': 'SCA', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        
        # === NIGHT STAFF (12) ===
        # Team A (4 staff) - 11 shifts/week
        {'sap': '000690', 'first_name': 'Jack', 'last_name': 'Henderson', 'role': 'SCWN', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000607', 'first_name': 'Wendy', 'last_name': 'Barnes', 'role': 'SCAN', 'unit': 'Pear', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000596', 'first_name': 'Olivia', 'last_name': 'Jones', 'role': 'SCAN', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000604', 'first_name': 'Victor', 'last_name': 'Kelly', 'role': 'SCAN', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team B (4 staff) - 10 shifts/week
        {'sap': '000623', 'first_name': 'George', 'last_name': 'Harrison', 'role': 'SCAN', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000634', 'first_name': 'Sophia', 'last_name': 'Hill', 'role': 'SCAN', 'unit': 'Pear', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000638', 'first_name': 'Willow', 'last_name': 'Nelson', 'role': 'SCAN', 'unit': 'Pear', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000627', 'first_name': 'Julia', 'last_name': 'Walker', 'role': 'SCAN', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team C (4 staff) - 10 shifts/week
        {'sap': '000702', 'first_name': 'Leo', 'last_name': 'Carter', 'role': 'SCWN', 'unit': 'Pear', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000659', 'first_name': 'Ivy', 'last_name': 'Bell', 'role': 'SCAN', 'unit': 'Pear', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000652', 'first_name': 'Natasha', 'last_name': 'Kaplinski', 'role': 'SCAN', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000642', 'first_name': 'Poppy', 'last_name': 'Saeed', 'role': 'SCAN', 'unit': 'Pear', 'contracted_hours': 22.5},  # 3 shifts/week
        
        # === PLUM UNIT - Real Staff Data ===
        # Day Staff (10) + Night Staff (11) = 21 total
        # === DAY STAFF (10) ===
        # Team A (3 staff) - 7 shifts/week
        {'sap': '000685', 'first_name': 'Chloe', 'last_name': 'Rogers', 'role': 'SCW', 'unit': 'Plum', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000594', 'first_name': 'Kyle', 'last_name': 'Oboe', 'role': 'SCA', 'unit': 'Plum', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000579', 'first_name': 'Katie', 'last_name': 'Reed', 'role': 'SCA', 'unit': 'Plum', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team B (4 staff) - 11 shifts/week
        {'sap': '000665', 'first_name': 'Carol', 'last_name': 'Williams', 'role': 'SCW', 'unit': 'Plum', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000587', 'first_name': 'Taylor', 'last_name': 'Henderson', 'role': 'SCA', 'unit': 'Plum', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000555', 'first_name': 'Uma', 'last_name': 'Lee', 'role': 'SCA', 'unit': 'Plum', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000546', 'first_name': 'Liam', 'last_name': 'Lopez', 'role': 'SCA', 'unit': 'Plum', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team C (3 staff) - 7 shifts/week
        {'sap': '000679', 'first_name': 'George', 'last_name': 'Allen', 'role': 'SCW', 'unit': 'Plum', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000567', 'first_name': 'Piper', 'last_name': 'Baker', 'role': 'SCA', 'unit': 'Plum', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000575', 'first_name': 'Xenia', 'last_name': 'Phillips', 'role': 'SCA', 'unit': 'Plum', 'contracted_hours': 15.0},  # 2 shifts/week
        # === NIGHT STAFF (11) ===
        # Team A (4 staff) - 10 shifts/week
        {'sap': '000692', 'first_name': 'Liam', 'last_name': 'Brooks', 'role': 'SCWN', 'unit': 'Plum', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000606', 'first_name': 'Nora', 'last_name': 'Gotyo', 'role': 'SCAN', 'unit': 'Plum', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000609', 'first_name': 'Yara', 'last_name': 'Henderson', 'role': 'SCAN', 'unit': 'Plum', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000598', 'first_name': 'Quinn', 'last_name': 'Oboe', 'role': 'SCAN', 'unit': 'Plum', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team B (4 staff) - 10 shifts/week
        {'sap': '000636', 'first_name': 'Ursula', 'last_name': 'Adams', 'role': 'SCAN', 'unit': 'Plum', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000629', 'first_name': 'Luna', 'last_name': 'Allen', 'role': 'SCAN', 'unit': 'Plum', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000625', 'first_name': 'Mark', 'last_name': 'Lewis', 'role': 'SCAN', 'unit': 'Plum', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000640', 'first_name': 'Xenia', 'last_name': 'Warrior', 'role': 'SCAN', 'unit': 'Plum', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team C (3 staff) - 8 shifts/week
        {'sap': '000698', 'first_name': 'Harry', 'last_name': 'Hall', 'role': 'SCWN', 'unit': 'Plum', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000644', 'first_name': 'Ruby', 'last_name': 'Rubia', 'role': 'SCAN', 'unit': 'Plum', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000661', 'first_name': 'Kyle', 'last_name': 'Son Ji', 'role': 'SCAN', 'unit': 'Plum', 'contracted_hours': 15.0},  # 2 shifts/week
        
        # === STRAWBERRY UNIT - Real Staff Data ===
        # Day Staff (11) + Night Staff (10) = 21 total
        # === DAY STAFF (11) ===
        # Team A (4 staff) - 10 shifts/week
        {'sap': '000689', 'first_name': 'Gemma', 'last_name': 'Bell', 'role': 'SCW', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000681', 'first_name': 'Yvonne', 'last_name': 'Evans', 'role': 'SCW', 'unit': 'Strawberry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000590', 'first_name': 'Adam', 'last_name': 'Bryant', 'role': 'SCA', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000583', 'first_name': 'Poppy', 'last_name': 'Cook', 'role': 'SCA', 'unit': 'Strawberry', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team B (3 staff) - 7 shifts/week
        {'sap': '000669', 'first_name': 'Grace', 'last_name': 'Miller', 'role': 'SCW', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000559', 'first_name': 'Yara', 'last_name': 'Harris', 'role': 'SCA', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000550', 'first_name': 'Peter', 'last_name': 'Thomas', 'role': 'SCA', 'unit': 'Strawberry', 'contracted_hours': 22.5},  # 3 shifts/week
        # Team C (4 staff) - 10 shifts/week
        {'sap': '000675', 'first_name': 'Caleb', 'last_name': 'Lewis', 'role': 'SCW', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000566', 'first_name': 'Oscar', 'last_name': 'Adams', 'role': 'SCA', 'unit': 'Strawberry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000571', 'first_name': 'Ursula', 'last_name': 'Campbell', 'role': 'SCA', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000562', 'first_name': 'Kyle', 'last_name': 'Torres', 'role': 'SCA', 'unit': 'Strawberry', 'contracted_hours': 22.5},  # 3 shifts/week
        # === NIGHT STAFF (10) ===
        # Team A (3 staff) - 7 shifts/week
        {'sap': '000602', 'first_name': 'Tina', 'last_name': 'Bailey', 'role': 'SCAN', 'unit': 'Strawberry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000617', 'first_name': 'Finn', 'last_name': 'Barr', 'role': 'SCAN', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000613', 'first_name': 'Ben', 'last_name': 'Nevis', 'role': 'SCAN', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team B (4 staff) - 9 shifts/week
        {'sap': '000696', 'first_name': 'JoJo', 'last_name': 'McArthur', 'role': 'SCWN', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000621', 'first_name': 'Ethan', 'last_name': 'Hawke', 'role': 'SCAN', 'unit': 'Strawberry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000641', 'first_name': 'Jacqui', 'last_name': 'Swan', 'role': 'SCAN', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
        {'sap': '000632', 'first_name': 'Ryan', 'last_name': 'Torres', 'role': 'SCAN', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
        # Team C (3 staff) - 8 shifts/week
        {'sap': '000650', 'first_name': 'Adam', 'last_name': 'Phillips', 'role': 'SCAN', 'unit': 'Strawberry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000648', 'first_name': 'Victor', 'last_name': 'Turner', 'role': 'SCAN', 'unit': 'Strawberry', 'contracted_hours': 22.5},  # 3 shifts/week
        {'sap': '000657', 'first_name': 'Grace', 'last_name': 'Ward', 'role': 'SCAN', 'unit': 'Strawberry', 'contracted_hours': 15.0},  # 2 shifts/week
    ]
    
    # Calculate start date (rolling window by default)
    if start_date is None:
        # Get current date and find the Sunday of current week
        today = datetime.now().date()
        # Calculate days since Sunday (0=Monday, 6=Sunday in Python)
        days_since_sunday = (today.weekday() + 1) % 7
        # Get this week's Sunday
        start_date = today - timedelta(days=days_since_sunday)
    
    date_range = [start_date + timedelta(days=i) for i in range(weeks * 7)]
    
    # Create pattern data structure
    pattern_data = {
        'staff': [],
        'dates': date_range,
        'weeks': weeks,
        'start_date': start_date
    }
    
    # REAL ORCHARD GROVE 3-WEEK ROTATING PATTERNS
    # SM/OM: Mon-Fri office hours (9am-5pm) - supernumerary
    # SSCW/SSCWN: Mon-Fri pattern - supernumerary senior coverage
    # Teams A/B/C rotate through 3-week cycle based on contracted hours
    
    # Base date for week calculation (first Sunday of 2026)
    base_date = datetime(2026, 1, 4).date()  # Sunday, Jan 4, 2026
    
    # Calculate which week we're in (0, 1, or 2 in the 3-week cycle)
    days_from_base = (start_date - base_date).days
    week_in_cycle = (days_from_base // 7) % 3
    
    # 3-WEEK ROTATING PATTERNS (Real Orchard Grove Schedule)
    # 3 shifts/week patterns:
    patterns_3shifts = {
        'A': [
            {'Sun': 'X', 'Mon': 'X', 'Tue': 'X', 'Wed': '', 'Thu': '', 'Fri': '', 'Sat': ''},  # Week 0: Sun/Mon/Tue
            {'Sun': '', 'Mon': '', 'Tue': '', 'Wed': '', 'Thu': 'X', 'Fri': 'X', 'Sat': 'X'},  # Week 1: Thu/Fri/Sat
            {'Sun': '', 'Mon': '', 'Tue': 'X', 'Wed': 'X', 'Thu': 'X', 'Fri': '', 'Sat': ''}   # Week 2: Tue/Wed/Thu
        ],
        'B': [
            {'Sun': '', 'Mon': '', 'Tue': '', 'Wed': '', 'Thu': 'X', 'Fri': 'X', 'Sat': 'X'},  # Week 0: Thu/Fri/Sat
            {'Sun': '', 'Mon': '', 'Tue': 'X', 'Wed': 'X', 'Thu': 'X', 'Fri': '', 'Sat': ''},  # Week 1: Tue/Wed/Thu
            {'Sun': 'X', 'Mon': 'X', 'Tue': 'X', 'Wed': '', 'Thu': '', 'Fri': '', 'Sat': ''}   # Week 2: Sun/Mon/Tue
        ],
        'C': [
            {'Sun': '', 'Mon': '', 'Tue': 'X', 'Wed': 'X', 'Thu': 'X', 'Fri': '', 'Sat': ''},  # Week 0: Tue/Wed/Thu
            {'Sun': 'X', 'Mon': 'X', 'Tue': 'X', 'Wed': '', 'Thu': '', 'Fri': '', 'Sat': ''},  # Week 1: Sun/Mon/Tue
            {'Sun': '', 'Mon': '', 'Tue': '', 'Wed': '', 'Thu': 'X', 'Fri': 'X', 'Sat': 'X'}   # Week 2: Thu/Fri/Sat
        ]
    }
    
    # 2 shifts/week patterns (consecutive days):
    patterns_2shifts = {
        'A': [
            {'Sun': 'X', 'Mon': 'X', 'Tue': '', 'Wed': '', 'Thu': '', 'Fri': '', 'Sat': ''},  # Week 0: Sun/Mon
            {'Sun': '', 'Mon': '', 'Tue': '', 'Wed': '', 'Thu': '', 'Fri': 'X', 'Sat': 'X'},  # Week 1: Fri/Sat
            {'Sun': '', 'Mon': '', 'Tue': 'X', 'Wed': 'X', 'Thu': '', 'Fri': '', 'Sat': ''}   # Week 2: Tue/Wed
        ],
        'B': [
            {'Sun': '', 'Mon': '', 'Tue': '', 'Wed': '', 'Thu': '', 'Fri': 'X', 'Sat': 'X'},  # Week 0: Fri/Sat
            {'Sun': '', 'Mon': '', 'Tue': 'X', 'Wed': 'X', 'Thu': '', 'Fri': '', 'Sat': ''},  # Week 1: Tue/Wed
            {'Sun': 'X', 'Mon': 'X', 'Tue': '', 'Wed': '', 'Thu': '', 'Fri': '', 'Sat': ''}   # Week 2: Sun/Mon
        ],
        'C': [
            {'Sun': '', 'Mon': '', 'Tue': 'X', 'Wed': 'X', 'Thu': '', 'Fri': '', 'Sat': ''},  # Week 0: Tue/Wed
            {'Sun': 'X', 'Mon': 'X', 'Tue': '', 'Wed': '', 'Thu': '', 'Fri': '', 'Sat': ''},  # Week 1: Sun/Mon
            {'Sun': '', 'Mon': '', 'Tue': '', 'Wed': '', 'Thu': '', 'Fri': 'X', 'Sat': 'X'}   # Week 2: Fri/Sat
        ]
    }
    
    # Management patterns (non-rotating)
    patterns_mgmt = {
        'SM': {'Mon': 'Office', 'Tue': 'Office', 'Wed': 'Office', 'Thu': 'Office', 'Fri': 'Office', 'Sat': '', 'Sun': ''},
        'OM': {'Mon': 'Office', 'Tue': 'Office', 'Wed': 'Office', 'Thu': 'Office', 'Fri': 'Office', 'Sat': '', 'Sun': ''},
        'SSCW': {'Mon': 'D', 'Tue': 'D', 'Wed': 'D', 'Thu': 'D', 'Fri': 'D', 'Sat': '', 'Sun': ''},  # Mon-Fri days
        'SSCWN': {'Mon': 'N', 'Tue': 'N', 'Wed': 'N', 'Thu': 'N', 'Fri': 'N', 'Sat': '', 'Sun': ''}  # Mon-Fri nights
    }
    
    # Orchard Grove units (for unit rotation display)
    units = ['Bramley', 'Cherry', 'Grape', 'Orange', 'Peach', 'Pear', 'Plum', 'Strawberry']
    
    # Build staff data with patterns
    for idx, staff in enumerate(staff_list):
        sap = staff['sap']
        name = f"{staff['first_name']} {staff['last_name']}"
        role = staff['role']
        unit = staff['unit']
        hours = staff['contracted_hours']
        
        # Determine team assignment (A/B/C based on SAP number)
        # Last digit: 0-2=A, 3-5=B, 6-9=C for fair distribution
        last_digit = int(sap[-1])
        if last_digit <= 2:
            team = 'A'
        elif last_digit <= 5:
            team = 'B'
        else:
            team = 'C'
        
        # Generate shifts for all dates
        shifts = []
        for date_idx, date in enumerate(date_range):
            day_name = date.strftime('%a')
            
            # Calculate which week of the 3-week cycle this date is in
            days_from_base_for_date = (date - base_date).days
            current_week_in_cycle = (days_from_base_for_date // 7) % 3
            
            # Select pattern based on role, team, and current week in cycle
            if role in ['SM', 'OM']:
                # Senior management use fixed Mon-Fri office pattern (supernumerary)
                pattern = patterns_mgmt[role]
            elif role == 'SSCW':  # Senior day staff - 3 shifts/week rotating
                base_pattern = patterns_3shifts[team][current_week_in_cycle]
                # Convert X to D for day shifts
                pattern = {day: ('D' if shift == 'X' else shift) for day, shift in base_pattern.items()}
            elif role == 'SSCWN':  # Senior night staff - 3 shifts/week rotating
                base_pattern = patterns_3shifts[team][current_week_in_cycle]
                # Convert X to N for night shifts
                pattern = {day: ('N' if shift == 'X' else shift) for day, shift in base_pattern.items()}
            elif role in ['SCW', 'SCA']:  # Day staff
                # Determine if 2 or 3 shifts based on contracted hours
                shifts_per_week = 2 if hours == 15.0 else 3
                if shifts_per_week == 3:
                    base_pattern = patterns_3shifts[team][current_week_in_cycle]
                else:
                    base_pattern = patterns_2shifts[team][current_week_in_cycle]
                # Convert X to D for day shifts
                pattern = {day: ('D' if shift == 'X' else shift) for day, shift in base_pattern.items()}
            elif role in ['SCWN', 'SCAN']:  # Night staff
                # Determine if 2 or 3 shifts based on contracted hours
                shifts_per_week = 2 if hours == 15.0 else 3
                if shifts_per_week == 3:
                    base_pattern = patterns_3shifts[team][current_week_in_cycle]
                else:
                    base_pattern = patterns_2shifts[team][current_week_in_cycle]
                # Convert X to N for night shifts
                pattern = {day: ('N' if shift == 'X' else shift) for day, shift in base_pattern.items()}
            else:
                pattern = {}
            
            # Apply pattern
            shift_code = pattern.get(day_name, '')
            
            if shift_code:
                # For SM/OM, keep their base unit (Management)
                # For others, rotate through units every 2 weeks
                if role in ['SM', 'OM']:
                    unit_name = unit  # Keep Management
                else:
                    week_num = date_idx // 7
                    unit_name = units[(idx + week_num // 2) % len(units)]
                
                shifts.append({
                    'date': date,
                    'type': 'shift',
                    'shift_code': shift_code,
                    'unit': unit_name
                })
            else:
                shifts.append({
                    'date': date,
                    'type': 'empty',
                    'unit': None
                })
        
        pattern_data['staff'].append({
            'sap': sap,
            'name': name,
            'role': role,
            'unit': unit,
            'contracted_hours': hours,
            'shifts': shifts
        })
    
    # Calculate senior staff coverage (SSCW/SSCWN) per date and shift type
    coverage = {}  # Key: (date, shift_type), Value: count
    for staff_member in pattern_data['staff']:
        role = staff_member['role']
        if role in ['SSCW', 'SSCWN']:
            for shift in staff_member['shifts']:
                if shift['type'] == 'shift' and shift['shift_code'] in ['D', 'N']:
                    date = shift['date']
                    shift_type = shift['shift_code']
                    key = (date, shift_type)
                    coverage[key] = coverage.get(key, 0) + 1
    
    pattern_data['senior_coverage'] = coverage
    
    # Calculate daily coverage summary for each date
    daily_coverage = []
    for date in date_range:
        day_summary = {
            'SSCW': 0,      # Senior day staff
            'Care': 0,      # Regular day staff (SCW + SCA)
            'SSCWN': 0,     # Senior night staff
            'Care N': 0     # Regular night staff (SCWN + SCAN)
        }
        
        for staff_member in pattern_data['staff']:
            role = staff_member['role']
            # Find shift for this date
            for shift in staff_member['shifts']:
                if shift['date'] == date and shift['type'] == 'shift':
                    shift_code = shift['shift_code']
                    
                    # Count day shifts
                    if shift_code == 'D':
                        if role == 'SSCW':
                            day_summary['SSCW'] += 1
                        elif role in ['SCW', 'SCA']:
                            day_summary['Care'] += 1
                    
                    # Count night shifts
                    elif shift_code == 'N':
                        if role == 'SSCWN':
                            day_summary['SSCWN'] += 1
                        elif role in ['SCWN', 'SCAN']:
                            day_summary['Care N'] += 1
                    
                    # Office hours (SM/OM) don't count in summary
                    break
        
        daily_coverage.append(day_summary)
    
    pattern_data['daily_coverage'] = daily_coverage
    
    # Sort staff by role hierarchy: SM/OM (office) → SSCW (day senior) → SCW/SCA (day care) → SSCWN (night senior) → SCWN/SCAN (night care)
    role_order = {
        'SM': 1,
        'OM': 2,
        'SSCW': 3,
        'SCW': 4,
        'SCA': 5,
        'SSCWN': 6,
        'SCWN': 7,
        'SCAN': 8
    }
    pattern_data['staff'].sort(key=lambda x: (role_order.get(x['role'], 99), x['name']))
    
    return pattern_data


# HTML Template
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pattern Overview Prototype - {{ data.weeks }} Weeks</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .header .info {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .controls {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .controls button {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            background: #667eea;
            color: white;
            cursor: pointer;
            font-size: 14px;
        }
        
        .controls button:hover {
            background: #5568d3;
        }
        
        .controls select {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .pattern-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .pattern-grid {
            display: grid;
            grid-template-columns: 300px 1fr;
            height: calc(100vh - 280px);
            overflow: hidden;
        }
        
        .staff-column {
            background: #f8f9fa;
            border-right: 2px solid #dee2e6;
            overflow-y: hidden;  /* Controlled by dates-container */
            position: sticky;
            left: 0;
            z-index: 100;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
        }
        
        .staff-list {
            overflow-y: auto;
            overflow-x: hidden;
            max-height: calc(100vh - 280px);
        }
        
        .staff-list::-webkit-scrollbar {
            display: none; /* Hide scrollbar for cleaner look */
        }
        
        .staff-list {
            -ms-overflow-style: none;  /* IE and Edge */
            scrollbar-width: none;  /* Firefox */
        }
        
        .dates-container {
            overflow-x: auto;
            overflow-y: auto;
            scroll-behavior: smooth;
        }
        
        .staff-header {
            background: #495057;
            color: white;
            padding: 8px 12px;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 50;
            display: flex;
            align-items: center;
            min-height: 130px;
            box-sizing: border-box;
        }
        
        .dates-header {
            background: #495057;
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 50;
            height: auto;
        }
        
        .dates-header {
            display: flex;
            min-width: fit-content;
            position: sticky;
            top: 0;
            background: #495057;
            z-index: 50;
        }
        
        .day-header {
            min-width: 80px;
            width: 80px;
            flex-shrink: 0;
            text-align: center;
            padding: 8px 4px;
            border-right: 1px solid #6c757d;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 130px;
            box-sizing: border-box;
        }
        
        .day-header.week-start {
            border-left: 3px solid #ffc107;
            background: #343a40;
        }
        
        .week-label-inline {
            font-size: 9px;
            font-weight: bold;
            color: #ffc107;
            margin-bottom: 4px;
            text-transform: uppercase;
        }
        
        .day-name {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 2px;
        }
        
        .day-date {
            font-size: 10px;
            opacity: 0.9;
        }
        
        .coverage-summary {
            font-size: 9px;
            margin-top: 4px;
            padding: 3px 4px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            line-height: 1.3;
        }
        
        .coverage-line {
            display: flex;
            justify-content: space-between;
            margin: 1px 0;
        }
        
        .coverage-count {
            font-weight: bold;
            color: #ffc107;
        }
        
        .staff-row {
            border-bottom: 1px solid #e9ecef;
            font-size: 10px;
            height: 60px;
            max-height: 60px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 0 8px;
            overflow: hidden;
            line-height: 1.2;
        }
        
        .staff-row.supernumerary {
            background: linear-gradient(90deg, #fef3e2 0%, #ffffff 100%);
            border-left: 3px solid #f59e0b;
        }
        
        .coverage-badge {
            position: absolute;
            bottom: 2px;
            right: 2px;
            font-size: 8px;
            background: #10b981;
            color: white;
            padding: 1px 3px;
            border-radius: 3px;
            font-weight: bold;
            opacity: 0.9;
        }
        
        .coverage-badge.warning {
            background: #ef4444;
            animation: pulse-warning 2s infinite;
        }
        
        .shift-cell.coverage-warning {
            border: 2px solid #ef4444 !important;
            box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
        }
        
        @keyframes pulse-warning {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .staff-name {
            font-weight: 600;
            color: #2c3e50;
            font-size: 11px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 2px;
        }
        
        .staff-info {
            font-size: 9px;
            color: #6c757d;
            margin: 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.2;
        }
        
        .shifts-row {
            display: flex;
            border-bottom: 1px solid #e9ecef;
            height: 60px;
            align-items: center;
        }
        
        .shift-cell {
            min-width: 80px;
            width: 80px;
            height: 60px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            border-right: 1px solid #e9ecef;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }
        
        .shift-cell.week-start {
            border-left: 3px solid #ffc107;
        }
        
        .shift-cell:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            z-index: 10;
        }
        
        .shift-cell.empty {
            background: white;
        }
        
        .shift-cell.office {
            background: #e3f2fd;
            color: #1565c0;
            font-size: 10px;
        }
        
        .shift-cell.leave {
            background: #c8e6c9;
            color: #2e7d32;
        }
        
        .shift-cell.sickness {
            background: #ffccbc;
            color: #d84315;
        }
        
        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        
        .modal-content {
            background-color: white;
            margin: 10% auto;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            max-width: 500px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }
        
        .modal-header h2 {
            margin: 0;
            color: #495057;
        }
        
        .close {
            color: #aaa;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            color: #000;
        }
        
        .modal-body {
            margin: 20px 0;
        }
        
        .modal-option {
            padding: 15px;
            margin: 10px 0;
            border: 2px solid #e9ecef;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .modal-option:hover {
            background: #f8f9fa;
            border-color: #667eea;
        }
        
        .modal-option h3 {
            margin: 0 0 5px 0;
            color: #495057;
        }
        
        .modal-option p {
            margin: 0;
            color: #6c757d;
            font-size: 14px;
        }
        
        /* Unit colors (Orchard Grove units) */
        .unit-pear { background: #f0f4c3; color: #689f38; }
        .unit-grape { background: #e1bee7; color: #7b1fa2; }
        .unit-orange { background: #ffe0b2; color: #ef6c00; }
        .unit-cherry { background: #ffcdd2; color: #c62828; }
        .unit-bramley { background: #c8e6c9; color: #2e7d32; }
        .unit-plum { background: #d1c4e9; color: #512da8; }
        .unit-peach { background: #ffccbc; color: #d84315; }
        .unit-strawberry { background: #f8bbd0; color: #ad1457; }
        
        .week-boundary {
            border-left: 2px solid #495057;
        }
        
        .legend {
            padding: 15px;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
            display: flex;
            gap: 20px;
            font-size: 12px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .legend-box {
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }
        
        .scroll-indicator {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            font-size: 12px;
            display: none;
        }
        
        .stats {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .stat-card {
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 12px;
            opacity: 0.9;
        }
        
        .stat-card.stat-warning {
            border-left: 3px solid #ef4444;
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            color: #991b1b;
        }
        
        .stat-card.stat-warning .stat-value {
            color: #ef4444;
        }
        
        /* Print Styles */
        @media print {
            body { background: white; }
            .controls, .legend, .stats { display: none !important; }
            .pattern-container { overflow: visible !important; }
            .dates-container { overflow: visible !important; }
            .staff-header, .dates-header { position: static !important; }
            .shift-cell, .staff-row { page-break-inside: avoid; }
        }
        
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="header">
        <h1>� Orchard Grove - Pattern Overview</h1>
        <div class="info">
            Real staff data from Bramley & Cherry units
            <br>
            {{ data.staff|length }} staff members: Bramley (18) + Cherry (20) | {{ data.dates|length }} days
        </div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{{ data.staff|length }}</div>
            <div class="stat-label">Total Staff</div>
            <div style="font-size: 9px; margin-top: 4px; opacity: 0.8;">3 Supernumerary ⭐ | 59 Regular</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ data.dates|length }}</div>
            <div class="stat-label">Days</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ (data.dates|length / 7)|int }}</div>
            <div class="stat-label">Weeks</div>
        </div>
        {% set low_coverage = [] %}
        {% for key, count in data.senior_coverage.items() %}
            {% if count < 2 %}
                {% set _ = low_coverage.append(1) %}
            {% endif %}
        {% endfor %}
        <div class="stat-card {% if low_coverage|length > 0 %}stat-warning{% endif %}">
            <div class="stat-value">{{ low_coverage|length }}</div>
            <div class="stat-label">Coverage Alerts</div>
            <div style="font-size: 9px; margin-top: 4px; opacity: 0.8;">Shifts with &lt;2 senior staff</div>
        </div>
    </div>
    
    <div class="controls">
        <button onclick="scrollToToday()">📅 Today</button>
        <button onclick="scrollToWeek('prev')">⬅️ Previous Week</button>
        <button onclick="scrollToWeek('next')">➡️ Next Week</button>
        <select onchange="jumpToWeek(this.value)">
            <option value="">Jump to Week...</option>
            {% for week_num in range(1, data.weeks + 1) %}
            <option value="{{ week_num }}">Week {{ week_num }}</option>
            {% endfor %}
        </select>
        <span style="margin: 0 15px; color: #6c757d;">|</span>
        <label for="startDate" style="font-size: 14px; color: #495057;">Start Date:</label>
        <input type="date" id="startDate" value="{{ data.start_date.strftime('%Y-%m-%d') }}" 
               onchange="changeStartDate(this.value)" 
               style="margin-left: 5px; padding: 5px 10px; border: 1px solid #ced4da; border-radius: 4px;">
        <button onclick="resetToCurrentWeek()" style="margin-left: 5px;">🔄 Current Week</button>
        <span style="margin: 0 15px; color: #6c757d;">|</span>
        <select id="shiftFilter" onchange="filterShifts(this.value)" style="margin-left: 5px;">
            <option value="all">All Shifts</option>
            <option value="D">Days Only</option>
            <option value="N">Nights Only</option>
        </select>
        <button onclick="printDailyAllocation()" style="margin-left: 10px;">🖨️ Print Daily Allocation</button>
        <span style="margin-left: auto; color: #6c757d; font-size: 14px;">
            Scroll Performance: <span id="fps">60</span> FPS
        </span>
    </div>
    
    <div class="pattern-container">
        <div class="pattern-grid">
            <!-- Sticky Staff Column -->
            <div class="staff-column">
                <div class="staff-header">
                    Staff Information
                </div>
                <div class="staff-list" id="staffList">
                {% for staff in data.staff %}
                <div class="staff-row {% if staff.role in ['SM', 'OM', 'SSCW', 'SSCWN'] %}supernumerary{% endif %}">
                    <div class="staff-name">
                        {{ staff.name }}
                        {% if staff.role in ['SM', 'OM', 'SSCW', 'SSCWN'] %}
                        <span style="font-size: 9px; color: #667eea; font-weight: bold;">⭐</span>
                        {% endif %}
                    </div>
                    <div class="staff-info">
                        {{ staff.sap }} | {{ staff.role }}
                        {% if staff.role in ['SM', 'OM', 'SSCW', 'SSCWN'] %}(Supernumerary){% endif %}
                        | {{ staff.unit }}
                    </div>
                </div>
                {% endfor %}
                </div>
            </div>
            
            <!-- Scrollable Dates Column -->
            <div class="dates-container" id="datesContainer">
                <!-- Date Headers -->
                <div class="dates-header">
                    {% for date in data.dates %}
                        {% set week_num = (loop.index0 // 7) + 1 %}
                        {% set is_sunday = date.weekday() == 6 %}
                        {% set week_end_date = date + timedelta(days=6) %}
                        
                        <div class="day-header {% if is_sunday %}week-start{% endif %}">
                            {% if is_sunday %}
                                <div class="week-label-inline">Week {{ week_num }}</div>
                            {% endif %}
                            <span class="day-name">{{ date.strftime('%a') }}</span>
                            <span class="day-date">{{ date.strftime('%d %b') }}</span>
                            {% set date_index = loop.index0 %}
                            {% set day_coverage = data.daily_coverage[date_index] %}
                            <div class="coverage-summary">
                                <div class="coverage-line">
                                    <span>SSCW:</span>
                                    <span class="coverage-count">{{ day_coverage['SSCW'] }}</span>
                                </div>
                                <div class="coverage-line">
                                    <span>Care:</span>
                                    <span class="coverage-count">{{ day_coverage['Care'] }}</span>
                                </div>
                                <div class="coverage-line">
                                    <span>SSCWN:</span>
                                    <span class="coverage-count">{{ day_coverage['SSCWN'] }}</span>
                                </div>
                                <div class="coverage-line">
                                    <span>Care N:</span>
                                    <span class="coverage-count">{{ day_coverage['Care N'] }}</span>
                                </div>
                            </div>
                        </div>
                    {% endfor %}
                </div>
                
                <!-- Shifts Grid -->
                {% for staff in data.staff %}
                {% set staff_index = loop.index0 %}
                <div class="shifts-row">
                    {% for shift in staff.shifts %}
                        {% set is_sunday = data.dates[loop.index0].weekday() == 6 %}
                        {% set week_class = 'week-start' if is_sunday else '' %}
                        
                        {% if shift.type == 'leave' %}
                            <div class="shift-cell leave {{ week_class }}" title="Annual Leave - {{ shift.date.strftime('%d %b %Y') }}">
                                A/L
                            </div>
                        {% elif shift.type == 'shift' %}
                            {% if shift.shift_code == 'Office' %}
                                <div class="shift-cell office {{ week_class }}" 
                                     title="{{ shift.unit }} - Office Hours (9am-5pm) - {{ shift.date.strftime('%d %b %Y') }}">
                                    Office
                                </div>
                            {% else %}
                                {% set coverage_key = (shift.date, shift.shift_code) %}
                                {% set senior_count = data.senior_coverage.get(coverage_key, 0) %}
                                {% set has_warning = senior_count < 2 and shift.shift_code in ['D', 'N'] %}
                                <div class="shift-cell shift unit-{{ shift.unit|lower }} {{ week_class }} {% if has_warning %}coverage-warning{% endif %}" 
                                     onclick="openShiftModal('{{ staff.name }}', '{{ shift.date.strftime('%d %b %Y') }}', '{{ shift.shift_code }}', '{{ shift.unit }}', {{ loop.index0 }}, {{ staff_index }})"
                                     title="{{ shift.unit }} - {{ shift.shift_code }} - {{ shift.date.strftime('%d %b %Y') }}{% if shift.shift_code in ['D', 'N'] %} | Senior Staff: {{ senior_count }}{% if has_warning %} ⚠️ BELOW MINIMUM{% endif %}{% endif %} - Click to edit">
                                    {{ shift.shift_code }}
                                </div>
                            {% endif %}
                        {% else %}
                            <div class="shift-cell empty {{ week_class }}"></div>
                        {% endif %}
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-box unit-pear"></div>
                <span>Pear</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unit-grape"></div>
                <span>Grape</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unit-orange"></div>
                <span>Orange</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unit-cherry"></div>
                <span>Cherry</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unit-bramley"></div>
                <span>Bramley</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unit-plum"></div>
                <span>Plum</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unit-peach"></div>
                <span>Peach</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unit-strawberry"></div>
                <span>Strawberry</span>
            </div>
            <div class="legend-item">
                <div class="legend-box leave"></div>
                <span>Annual Leave</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background: #ffccbc;"></div>
                <span>Sickness</span>
            </div>
            <div class="legend-item">
                <div class="legend-box office"></div>
                <span>Office Hours (9am-5pm)</span>
            </div>
            <div class="legend-item">
                <span style="color: #667eea; font-weight: bold; font-size: 14px;">⭐</span>
                <span>Supernumerary Staff (SM, OM, SSCW, SSCWN - not counted in staffing ratios)</span>
            </div>
            <div class="legend-item">
                <span style="background: #10b981; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold;">2👥</span>
                <span>Senior Staff Coverage (SSCW/SSCWN count per shift)</span>
            </div>
            <div class="legend-item">
                <span style="background: #ef4444; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold;">1👥</span>
                <span>⚠️ Coverage Warning (minimum 2 senior staff required)</span>
            </div>
            <div class="legend-item">
                <span style="margin-left: auto; color: #6c757d; font-weight: bold;">D = Days (07:45-20:00) | N = Nights (19:45-08:00)</span>
            </div>
        </div>
    </div>
    
    <!-- Shift Edit Modal -->
    <div id="shiftModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Edit Shift</h2>
                <span class="close" onclick="closeShiftModal()">&times;</span>
            </div>
            <div class="modal-body">
                <div id="modalStaffInfo" style="margin-bottom: 20px; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                    <strong id="modalStaffName"></strong><br>
                    <span id="modalShiftDate" style="color: #6c757d;"></span>
                </div>
                
                <div class="modal-option" onclick="changeToAnnualLeave()">
                    <h3>🌴 Annual Leave</h3>
                    <p>Convert this shift to annual leave</p>
                </div>
                
                <div class="modal-option" onclick="changeToSickness()">
                    <h3>🩹 Sickness</h3>
                    <p>Mark this shift as sickness absence</p>
                </div>
                
                <div class="modal-option">
                    <h3>🏥 Change Unit</h3>
                    <p>Assign to a different unit</p>
                    <select id="unitSelector" style="width: 100%; padding: 8px; margin-top: 10px; border: 1px solid #ced4da; border-radius: 4px;" onchange="changeUnit(this.value)">
                        <option value="">Select unit...</option>
                        <option value="Pear">Pear</option>
                        <option value="Grape">Grape</option>
                        <option value="Orange">Orange</option>
                        <option value="Cherry">Cherry</option>
                        <option value="Bramley">Bramley</option>
                        <option value="Plum">Plum</option>
                        <option value="Peach">Peach</option>
                        <option value="Strawberry">Strawberry</option>
                    </select>
                </div>
            </div>
        </div>
    </div>
    
    <div class="scroll-indicator" id="scrollIndicator">
        Scrolling...
    </div>
    
    <script>
        const container = document.getElementById('datesContainer');
        const staffList = document.getElementById('staffList');
        const scrollIndicator = document.getElementById('scrollIndicator');
        let scrollTimeout;
        let lastScrollTime = Date.now();
        let frameCount = 0;
        
        // Synchronize staff column vertical scroll with dates container
        container.addEventListener('scroll', () => {
            staffList.scrollTop = container.scrollTop;
        });
        
        // Show/hide scroll indicator
        container.addEventListener('scroll', () => {
            scrollIndicator.style.display = 'block';
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                scrollIndicator.style.display = 'none';
            }, 1000);
            
            // Update FPS counter
            frameCount++;
            const now = Date.now();
            if (now - lastScrollTime >= 1000) {
                document.getElementById('fps').textContent = frameCount;
                frameCount = 0;
                lastScrollTime = now;
            }
        });
        
        // Scroll to today (first day in prototype)
        function scrollToToday() {
            container.scrollLeft = 0;
        }
        
        // Scroll by week
        function scrollToWeek(direction) {
            const dayWidth = 80; // px (updated from 60)
            const weekWidth = dayWidth * 7;
            if (direction === 'prev') {
                container.scrollLeft -= weekWidth;
            } else {
                container.scrollLeft += weekWidth;
            }
        }
        
        // Jump to specific week
        function jumpToWeek(weekNum) {
            if (!weekNum) return;
            const dayWidth = 80; // px (updated from 60)
            const targetScroll = (weekNum - 1) * 7 * dayWidth;
            container.scrollTo({
                left: targetScroll,
                behavior: 'smooth'
            });
        }
        
        // Filter shifts by type (Days/Nights)
        function filterShifts(filterType) {
            const allRows = document.querySelectorAll('.shifts-row');
            const allStaffRows = document.querySelectorAll('.staff-row');
            
            allRows.forEach((row, index) => {
                const staffRow = allStaffRows[index];
                const shiftCells = row.querySelectorAll('.shift-cell.shift');
                
                // Check if this staff member has the filtered shift type
                let hasFilteredShift = false;
                shiftCells.forEach(cell => {
                    const cellText = cell.textContent.trim();
                    // Check if cell starts with D or N (ignoring coverage badges)
                    const shiftType = cellText.charAt(0);
                    if (filterType === 'all' || shiftType === filterType) {
                        hasFilteredShift = true;
                    }
                });
                
                // Show/hide staff row and shift row based on filter
                if (filterType === 'all' || hasFilteredShift) {
                    row.classList.remove('hidden');
                    staffRow.classList.remove('hidden');
                } else {
                    row.classList.add('hidden');
                    staffRow.classList.add('hidden');
                }
            });
        }
        
        // Print daily allocation sheet
        function printDailyAllocation() {
            const today = new Date();
            const dateStr = today.toLocaleDateString('en-GB', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
            
            // Get current filter
            const filterSelect = document.getElementById('shiftFilter');
            const currentFilter = filterSelect ? filterSelect.value : 'all';
            const filterLabel = currentFilter === 'D' ? 'Day Shifts Only' : 
                               currentFilter === 'N' ? 'Night Shifts Only' : 'All Shifts';
            
            // Create print window
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Daily Allocation Sheet - ${filterLabel} - ${dateStr}</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        h1 { text-align: center; margin-bottom: 30px; }
                        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                        th, td { border: 1px solid #333; padding: 10px; text-align: left; }
                        th { background: #667eea; color: white; }
                        .unit-bluebell { background: #e3f2fd; }
                        .unit-primrose { background: #fff9c4; }
                        .unit-daffodil { background: #fff3e0; }
                        .unit-jasmine { background: #f3e5f5; }
                        .unit-rose { background: #fce4ec; }
                        .shift-D { font-weight: bold; color: #1565c0; }
                        .shift-N { font-weight: bold; color: #6a1b9a; }
                    </style>
                </head>
                <body>
                    <h1>Daily Staff Allocation Sheet</h1>
                    <p><strong>Date:</strong> ${dateStr}</p>
                    <p><strong>Filter:</strong> ${filterLabel}</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Staff Name</th>
                                <th>SAP</th>
                                <th>Role</th>
                                <th>Shift Type</th>
                                <th>Unit Assignment</th>
                            </tr>
                        </thead>
                        <tbody>
            `);
            
            // Get all staff and their current shifts
            const staffRows = document.querySelectorAll('.staff-row');
            const shiftRows = document.querySelectorAll('.shifts-row');
            
            staffRows.forEach((staffRow, index) => {
                if (staffRow.classList.contains('hidden')) return;
                
                const name = staffRow.querySelector('.staff-name').textContent;
                const info = staffRow.querySelector('.staff-info').textContent;
                const [sap, role, unit] = info.split(' | ');
                
                // Find first shift that matches current filter
                const shiftCells = shiftRows[index].querySelectorAll('.shift-cell.shift');
                let matchingShift = null;
                
                for (let cell of shiftCells) {
                    const cellText = cell.textContent.trim();
                    const shiftType = cellText.charAt(0);
                    if (currentFilter === 'all' || shiftType === currentFilter) {
                        matchingShift = cell;
                        break;
                    }
                }
                
                if (matchingShift) {
                    const shiftText = matchingShift.textContent.trim();
                    const shiftType = shiftText.charAt(0);
                    const shiftUnit = matchingShift.title.split(' - ')[0];
                    const shiftTimes = shiftType === 'D' ? '07:45-20:00' : '19:45-08:00';
                    
                    printWindow.document.write(`
                        <tr>
                            <td>${name}</td>
                            <td>${sap}</td>
                            <td>${role}</td>
                            <td class="shift-${shiftType}">${shiftType === 'D' ? 'Days' : 'Nights'} (${shiftTimes})</td>
                            <td>${shiftUnit}</td>
                        </tr>
                    `);
                }
            });
            
            printWindow.document.write(`
                        </tbody>
                    </table>
                    <p style="margin-top: 30px; font-size: 12px; color: #666;">
                        <strong>Legend:</strong> D = Days (07:45-20:00) | N = Nights (19:45-08:00)
                    </p>
                </body>
                </html>
            `);
            
            printWindow.document.close();
            printWindow.focus();
            
            // Wait for content to load, then print
            setTimeout(() => {
                printWindow.print();
            }, 250);
        }
        
        // Change start date and reload
        function changeStartDate(dateStr) {
            if (dateStr) {
                // Parse the date
                const selectedDate = new Date(dateStr + 'T00:00:00');
                
                // Find the Sunday of that week
                const dayOfWeek = selectedDate.getDay(); // 0=Sunday, 1=Monday, etc.
                const sunday = new Date(selectedDate);
                sunday.setDate(selectedDate.getDate() - dayOfWeek);
                
                // Format as YYYY-MM-DD
                const year = sunday.getFullYear();
                const month = String(sunday.getMonth() + 1).padStart(2, '0');
                const day = String(sunday.getDate()).padStart(2, '0');
                const sundayStr = `${year}-${month}-${day}`;
                
                // Reload with custom start date parameter
                window.location.href = `?start=${sundayStr}`;
            }
        }
        
        // Reset to current week (rolling window)
        function resetToCurrentWeek() {
            // Remove start parameter to use default rolling window
            window.location.href = window.location.pathname;
        }
        
        // Shift editing variables
        let currentEditingCell = null;
        let currentStaffIndex = null;
        let currentShiftIndex = null;
        
        // Open shift edit modal
        function openShiftModal(staffName, shiftDate, shiftCode, unit, shiftIndex, staffIndex) {
            currentStaffIndex = staffIndex;
            currentShiftIndex = shiftIndex;
            
            // Find and store the cell reference
            const rows = document.querySelectorAll('.shifts-row');
            const row = rows[staffIndex];
            const cells = row.querySelectorAll('.shift-cell');
            currentEditingCell = cells[shiftIndex];
            
            // Populate modal
            document.getElementById('modalStaffName').textContent = staffName;
            document.getElementById('modalShiftDate').textContent = shiftDate + ' - ' + shiftCode + ' shift';
            document.getElementById('unitSelector').value = unit;
            
            // Show modal
            document.getElementById('shiftModal').style.display = 'block';
        }
        
        // Close modal
        function closeShiftModal() {
            document.getElementById('shiftModal').style.display = 'none';
            currentEditingCell = null;
            currentStaffIndex = null;
            currentShiftIndex = null;
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('shiftModal');
            if (event.target == modal) {
                closeShiftModal();
            }
        }
        
        // Change to annual leave
        function changeToAnnualLeave() {
            if (currentEditingCell) {
                currentEditingCell.className = 'shift-cell leave';
                if (currentEditingCell.classList.contains('week-start')) {
                    currentEditingCell.classList.add('week-start');
                }
                currentEditingCell.textContent = 'A/L';
                currentEditingCell.title = 'Annual Leave';
                currentEditingCell.onclick = null; // Remove click handler for leave
            }
            closeShiftModal();
        }
        
        // Change to sickness
        function changeToSickness() {
            if (currentEditingCell) {
                currentEditingCell.className = 'shift-cell sickness';
                if (currentEditingCell.classList.contains('week-start')) {
                    currentEditingCell.classList.add('week-start');
                }
                currentEditingCell.textContent = 'SICK';
                currentEditingCell.title = 'Sickness Absence';
                currentEditingCell.onclick = null; // Remove click handler for sickness
            }
            closeShiftModal();
        }
        
        // Change unit
        function changeUnit(newUnit) {
            if (currentEditingCell && newUnit) {
                // Remove old unit class
                currentEditingCell.classList.forEach(cls => {
                    if (cls.startsWith('unit-')) {
                        currentEditingCell.classList.remove(cls);
                    }
                });
                
                // Add new unit class
                currentEditingCell.classList.add('unit-' + newUnit.toLowerCase());
                
                // Update title
                const shiftCode = currentEditingCell.textContent.trim();
                const dateMatch = currentEditingCell.title.match(/\\d{2} \\w{3} \\d{4}/);
                const date = dateMatch ? dateMatch[0] : '';
                currentEditingCell.title = newUnit + ' - ' + shiftCode + ' - ' + date + ' - Click to edit';
                
                // Close modal
                closeShiftModal();
            }
        }
        
        // Performance monitoring
        console.log('Pattern Overview Prototype Loaded');
        console.log('Total cells:', {{ data.dates|length * data.staff|length }});
        console.log('Weeks:', {{ data.weeks }});
        console.log('Days:', {{ data.dates|length }});
        console.log('Staff:', {{ data.staff|length }});
        
        // Measure initial render time
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Load time:', perfData.loadEventEnd - perfData.fetchStart, 'ms');
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Render prototype with 12 weeks (rolling window by default)"""
    from datetime import timedelta as td
    from flask import request
    
    # Check if custom start date provided
    start_param = request.args.get('start')
    start_date = None
    
    if start_param:
        try:
            # Parse YYYY-MM-DD format
            start_date = datetime.strptime(start_param, '%Y-%m-%d').date()
        except ValueError:
            pass  # Invalid date, use default rolling window
    
    data = generate_mock_data(weeks=12, start_date=start_date)
    return render_template_string(TEMPLATE, data=data, timedelta=td)

@app.route('/<int:weeks>')
def custom_weeks(weeks):
    """Render prototype with custom week count"""
    from datetime import timedelta as td
    from flask import request
    
    weeks = min(max(weeks, 3), 52)  # Clamp between 3 and 52
    
    # Check if custom start date provided
    start_param = request.args.get('start')
    start_date = None
    
    if start_param:
        try:
            start_date = datetime.strptime(start_param, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    data = generate_mock_data(weeks=weeks, start_date=start_date)
    
    # Add warning for large week counts
    if weeks > 26:
        print(f"⚠️  WARNING: Rendering {weeks} weeks ({weeks * 7} days) may be slow!")
        print(f"   Total cells: {weeks * 7 * 10} - Consider using 12-26 weeks for better performance")
    
    return render_template_string(TEMPLATE, data=data, timedelta=td)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔬 PATTERN OVERVIEW PROTOTYPE SERVER (STANDALONE)")
    print("="*60)
    print("\n📍 Access the prototype at:")
    print("   http://127.0.0.1:5001/        - 12 weeks (default)")
    print("   http://127.0.0.1:5001/4       - 4 weeks")
    print("   http://127.0.0.1:5001/26      - 26 weeks (6 months)")
    print("   http://127.0.0.1:5001/52      - 52 weeks (1 year)")
    print("\n✨ Features to test:")
    print("   - Sticky staff column (stays visible while scrolling)")
    print("   - Smooth horizontal scrolling")
    print("   - Navigation buttons (Today, Prev Week, Next Week)")
    print("   - Week selector dropdown")
    print("   - FPS counter (scroll performance)")
    print("   - Hover effects on shift cells")
    print("   - Week boundaries (darker vertical lines)")
    print("\n⚙️  Mock data: 10 staff, 5 patterns, rotating units, annual leave")
    print("🔓 NO Django/AXES - Pure Flask on port 5001")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=False, port=5001, use_reloader=False, host='127.0.0.1')
