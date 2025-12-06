# Sheep-Tracker
-----------------
A Telegram bot for tracking and analyzing sheep (for my dad).

## Features
- No user registration (single user — my dad)
- Add sheep records
- Delete sheep records
- Analyze statistics
- View list of sheep

## User Flow
1. User enters the bot.
2. Add a new sheep (name, date, weight, price, bought from).
3. Delete a sheep (user sees the list and chooses the sheep number to delete).
4. View the list of sheep (number, name, price, weight, date, and source).
5. View statistics (total sheep, total price, average weight, average price).

## Tech Stack
- Language: Python 3.10.12
- Database: simple JSON file (for now)

## Installation
1. Clone the repository:
```bash
git clone https://github.com/dev-azimjon-tech/sheep-tracker.git
cd sheep-tracker
```
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Start the bot:
```bash
python main.py
```
If you use a custom command such as `runserver`, run `python main.py runserver` only if you've configured it.