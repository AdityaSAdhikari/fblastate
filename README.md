# CityPulse

A local business directory desktop application built with Python and Tkinter for FBLA.

## Features

- **Account System** — Register as a Customer or Business Owner, log in, and log out
- **Business Listings** — Browse businesses with thumbnails, names, and star ratings
- **Business Details** — View full details including location, category, description, image, and reviews
- **Reviews & Ratings** — Customers can submit a star rating (1–5) and written review for any business
- **Search & Filter** — Search by name/description, filter by category, and sort by rating
- **Owner Tools** — Owners can create new business listings (with image upload) and edit existing ones
- **Persistent Storage** — All data is saved to `accounts.csv` and `businesses.csv`

## Requirements

- Python 3.x
- [pandas](https://pandas.pydata.org/)
- [Pillow](https://python-pillow.org/)

Install dependencies:

```bash
pip install pandas Pillow
```

## Running the App

```bash
python FBLASTATE.py
```

## Usage

1. Launch the app — you'll see **Login** and **Create New Account** buttons
2. Create an account and select your account type:
   - **Customer** — browse businesses, view details, leave reviews
   - **Owner** — everything a customer can do, plus create and edit your business listings
3. On the home screen, use the search bar, category dropdown, and rating sort to find businesses
4. Click **View Details** on any business card to see full info and past reviews
5. Click **Add Review** to leave a star rating and written review

## Data Files

| File | Description |
|------|-------------|
| `accounts.csv` | Stores user accounts (username, password, email, type, reviews) |
| `businesses.csv` | Stores business listings (name, location, image path, description, category, rating, reviews) |

These files are created automatically on first run and updated whenever data changes.
