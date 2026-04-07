#import all libraries and external sources
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
from PIL import Image, ImageTk
import os
import ast
import re
import io
import urllib.request
import ssl
import datetime
from tkinter import font as tkfont

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_CSV = os.path.join(APP_DIR, "accounts.csv")
BUSINESSES_CSV = os.path.join(APP_DIR, "businesses.csv")
REVIEWS_CSV = os.path.join(APP_DIR, "reviews.csv")

# DESIGN SYSTEM
BG         = "#f0f4f8"
HEADER_BG  = "#1e3a5f"
TOOLBAR_BG = "#16305a"
CARD_BG    = "#ffffff"
CARD_HOVER = "#eff6ff"
BORDER     = "#d1dce8"
PRIMARY    = "#2563eb"
PRIMARY_DK = "#1d4ed8"
TEXT_DK    = "#1e293b"
TEXT_MD    = "#475569"
TEXT_LT    = "#94a3b8"
WHITE      = "#ffffff"
SUCCESS    = "#16a34a"
ERROR_RED  = "#dc2626"
STAR_GOLD  = "#f59e0b"
INPUT_BG   = "#ffffff"
INPUT_BD   = "#cbd5e1"

FONT_TITLE = ("Segoe UI", 28, "bold")
FONT_H1    = ("Segoe UI", 16, "bold")
FONT_H2    = ("Segoe UI", 13, "bold")
FONT_BODY  = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)
FONT_BTN   = ("Segoe UI", 11, "bold")
FONT_CARD  = ("Segoe UI", 12, "bold")
FONT_TB    = ("Segoe UI", 10, "bold")

SHADOW      = "#c8d4e0"   # card shadow color
CHIP_BG     = "#f1f5f9"   # chip/tag background

CATEGORY_COLORS = {
    "Food":                  "#ef4444",
    "Service":               "#3b82f6",
    "Retail":                "#8b5cf6",
    "Health & Wellness":     "#10b981",
    "Education":             "#f59e0b",
    "Automotive":            "#64748b",
    "Travel & Hospitality":  "#06b6d4",
    "Entertainment":         "#ec4899",
    "Home Services":         "#f97316",
}

def getCategoryColor(category):
    return CATEGORY_COLORS.get(str(category).strip(), PRIMARY)

AVATAR_COLORS = ["#ef4444","#3b82f6","#8b5cf6","#10b981","#f59e0b","#ec4899","#06b6d4","#f97316","#64748b"]

def getAvatarColor(username):
    if not username or username == "Anonymous":
        return "#94a3b8"
    return AVATAR_COLORS[hash(username) % len(AVATAR_COLORS)]

def makeStarRow(parent, bg, rating, num_reviews):
    """Pack a Yelp-style star + rating + count row into parent."""
    f = Frame(parent, bg=bg)
    f.pack(fill="x", pady=(3, 0))
    filled = round(rating)
    stars = "★" * filled + "☆" * (5 - filled)
    Label(f, text=stars, font=("Segoe UI", 13), fg=STAR_GOLD, bg=bg).pack(side="left")
    Label(f, text=f"  {rating:.1f}", font=("Segoe UI", 11, "bold"), fg=TEXT_DK, bg=bg).pack(side="left")
    Label(f, text=f"  ({num_reviews} review{'s' if num_reviews != 1 else ''})",
          font=("Segoe UI", 10), fg=TEXT_LT, bg=bg).pack(side="left")
    return f

def isVerified(row):
    """Return True if the business has a non-empty License."""
    try:
        val = row.get("License", "") if hasattr(row, "get") else row["License"]
        return bool(val) and str(val).strip() not in ("", "nan")
    except:
        return False

# TTK STYLE
def applyStyles():
    """Configure ttk widget styles to match the app design system."""
    style = ttk.Style()
    style.theme_use("clam")  # "clam" is the most customizable built-in theme
    style.configure("TCombobox",
        fieldbackground=INPUT_BG, background=INPUT_BG,
        foreground=TEXT_DK, bordercolor=INPUT_BD,
        lightcolor=INPUT_BD, darkcolor=INPUT_BD,
        relief="flat", padding=(8, 6), font=FONT_BODY)
    # Prevent readonly comboboxes from reverting to grey background
    style.map("TCombobox", fieldbackground=[("readonly", INPUT_BG)])

# WIDGET HELPERS
def makeButton(parent, text, command, style="primary", width=None):
    """Create a flat, hover-animated button with a named style preset."""
    if style == "primary":  bg, abg = PRIMARY, PRIMARY_DK
    elif style == "ghost":  bg, abg = "#eff6ff", "#dbeafe"
    elif style == "danger": bg, abg = ERROR_RED, "#b91c1c"
    elif style == "success":bg, abg = SUCCESS, "#15803d"
    elif style == "toolbar":bg, abg = TOOLBAR_BG, PRIMARY
    elif style == "blac": bg, abg = "black", "#000000"
    else:                   bg, abg = PRIMARY, PRIMARY_DK
    fg = "black"
    afg = "red"  # hover foreground is always red for visual pop
    kw = dict(text=text, command=command, font=FONT_BTN,
              bg=bg, fg=fg, activebackground=abg, activeforeground=afg,
              relief="flat", cursor="hand2", bd=0, padx=16, pady=8)
    if width: kw["width"] = width
    btn = Button(parent, **kw)
    # Bind hover manually because activebackground only triggers on click in some OS themes
    btn.bind("<Enter>", lambda e: btn.config(bg=abg, fg="red"))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg, fg=fg))
    return btn

def isDarkColor(hex_color):
    """Return True if the hex color is dark enough to warrant white text."""
    c = hex_color.lstrip("#")
    if len(c) != 6:
        return False
    r = int(c[0:2], 16)
    g = int(c[2:4], 16)
    b = int(c[4:6], 16)
    # Standard relative luminance formula (ITU-R BT.601)
    luminance = (0.299 * r) + (0.587 * g) + (0.114 * b)
    return luminance < 150

def makeEntry(parent, width=30, show=None):
    """Create a styled flat Entry widget; pass show='*' for password fields."""
    kw = dict(font=FONT_BODY, bg=INPUT_BG, fg=TEXT_DK,
              insertbackground=TEXT_DK, relief="flat",
              highlightthickness=1, highlightbackground=INPUT_BD,
              highlightcolor=PRIMARY, bd=0, width=width)
    if show: kw["show"] = show
    return Entry(parent, **kw)

def addPlaceholder(entry, placeholderText):
    """Insert grey placeholder text that clears on focus and restores on blur."""
    entry.insert(0, placeholderText)
    entry.config(fg="grey")
    def on_focus_in(event):
        # Only clear if the placeholder is still showing
        if entry.get() == placeholderText:
            entry.delete(0, END)
            entry.config(fg=TEXT_DK)
    def on_focus_out(event):
        # Restore placeholder when the field is left empty
        if entry.get() == "":
            entry.insert(0, placeholderText)
            entry.config(fg="grey")
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def addTextPlaceholder(text_widget, placeholder):
    """Insert grey placeholder text into a Text widget with focus/blur handling."""
    text_widget.insert("1.0", placeholder)
    text_widget.config(fg="grey")
    def on_focus_in(event):
        # "1.0" to "end-1c" reads all text minus the trailing newline tkinter appends
        if text_widget.get("1.0", "end-1c") == placeholder:
            text_widget.delete("1.0", END)
            text_widget.config(fg=TEXT_DK)
    def on_focus_out(event):
        if text_widget.get("1.0", "end-1c") == "":
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg="grey")
    text_widget.bind("<FocusIn>", on_focus_in)
    text_widget.bind("<FocusOut>", on_focus_out)

# clearScreen — hides all children of mainContent
def clearScreen():
    """Hide all widgets currently packed in mainContent."""
    for widget in mainContent.winfo_children():
        widget.pack_forget()

def flushLayout():
    """Force pending geometry/layout work so screens render immediately."""
    try:
        startScreen.update_idletasks()
    except:
        pass
    try:
        businessViewer.configure(scrollregion=businessViewer.bbox("all"))
    except:
        pass

def businessNameExists(name, exclude_index=None):
    """Return True if a business with this name already exists (case-insensitive).

    exclude_index lets the edit form skip the business being edited so it
    does not flag its own current name as a duplicate.
    """
    target = str(name).strip().casefold()
    if not target or "Name" not in businessDatabase.columns:
        return False
    for idx, existing in businessDatabase["Name"].items():
        # Skip the row being edited to allow saving without changing the name
        if exclude_index is not None and idx == exclude_index:
            continue
        if str(existing).strip().casefold() == target:
            return True
    return False

activeScrollCanvas = None
browsePage = 0
browsePageSize = 24
browseData = None
thumbCache = {}
imageFailLog = set()

def setActiveScrollCanvas(canvas):
    """Track which canvas should receive global mousewheel events."""
    global activeScrollCanvas
    activeScrollCanvas = canvas

def smoothScrollByPixels(canvas, pixels):
    """Move a canvas by pixel distance for smoother wheel behavior.

    yview_moveto requires a fraction (0.0–1.0), so we convert pixel
    deltas manually using the content height as the scale factor.
    """
    if canvas is None or pixels == 0:
        return
    canvas.update_idletasks()
    region = canvas.bbox("all")
    if not region:
        return
    content_h = max(1, region[3] - region[1])
    view_h = max(1, canvas.winfo_height())
    max_offset = max(0, content_h - view_h)
    if max_offset <= 0:  # content fits entirely in view; no scrolling needed
        return
    top_frac = canvas.yview()[0]
    current_top = top_frac * max_offset
    new_top = max(0, min(max_offset, current_top + pixels))
    canvas.yview_moveto(new_top / max_offset)

def scrollCanvasFromEvent(canvas, event):
    """Translate a platform mousewheel event into a pixel scroll amount.

    Linux fires Button-4/5 events; Windows/macOS fire event.delta.
    Windows delta is a multiple of 120; macOS sends smaller fractional values.
    """
    if canvas is None:
        return
    pixels = 0
    if hasattr(event, "num") and event.num == 4:   # Linux scroll up
        pixels = -48
    elif hasattr(event, "num") and event.num == 5:  # Linux scroll down
        pixels = 48
    elif hasattr(event, "delta") and event.delta:
        if abs(event.delta) >= 120:  # Windows-style: delta is multiple of 120
            pixels = int((-event.delta / 120) * 56)
        else:  # macOS trackpad: delta is a small float
            pixels = int(-event.delta * 1.3)
    if pixels:
        smoothScrollByPixels(canvas, pixels)

def onGlobalMousewheel(event):
    """Route global mousewheel events to whichever canvas the cursor is over."""
    scrollCanvasFromEvent(activeScrollCanvas, event)
    # Return "break" to stop the event propagating to the default tkinter handler
    if activeScrollCanvas is not None:
        return "break"

def updateBrowsePager(total_results):
    """Refresh the pagination label and enable/disable prev/next buttons."""
    # Guard against being called before the UI widgets are created
    if "pageInfoLabel" not in globals():
        return
    max_page = max(0, (total_results - 1) // browsePageSize) if total_results else 0
    pageInfoLabel.config(text=f"Page {browsePage + 1}/{max_page + 1} ({total_results} results)")
    prevPageButton.config(state=(NORMAL if browsePage > 0 else DISABLED))
    nextPageButton.config(state=(NORMAL if browsePage < max_page else DISABLED))

def changeBrowsePage(delta):
    """Advance or retreat the browse page by delta, then re-render."""
    global browsePage, browseData
    # Re-use last filtered dataset rather than resetting to full list
    if browseData is None:
        browseData = businessDatabase.reset_index(drop=True)
    total = len(browseData)
    max_page = max(0, (total - 1) // browsePageSize) if total else 0
    # Clamp to valid range; passing no df keeps the existing browseData filter
    browsePage = max(0, min(max_page, browsePage + delta))
    showBusinesses()

# TOOLBAR (shown when logged in as Owner)
def showToolbar():
    """Show the owner action toolbar below the header."""
    toolbar.pack(fill="x", side="top")
    for w in toolbar.winfo_children():
        w.destroy()

    # Home button
    homeFg = "black"
    homeHoverFg = "red"
    homeBtn = Button(toolbar, text="🏠  Home", font=FONT_TB,
                     bg=TOOLBAR_BG, fg=homeFg, activebackground=PRIMARY,
                     activeforeground=homeHoverFg, relief="flat", cursor="hand2",
                     bd=0, padx=18, pady=10, command=setHomeScreen)
    homeBtn.bind("<Enter>", lambda e: homeBtn.config(bg=PRIMARY, fg=homeHoverFg))
    homeBtn.bind("<Leave>", lambda e: homeBtn.config(bg=TOOLBAR_BG, fg=homeFg))
    homeBtn.pack(side="left")

    sep1 = Label(toolbar, text="|", font=FONT_TB, fg=TEXT_LT, bg=TOOLBAR_BG, padx=4)
    sep1.pack(side="left")

    # Add Business button
    addFg = "black"
    addHoverFg = "red"
    addBtn = Button(toolbar, text="＋  Add Business", font=FONT_TB,
                    bg=TOOLBAR_BG, fg=addFg, activebackground=PRIMARY,
                    activeforeground=addHoverFg, relief="flat", cursor="hand2",
                    bd=0, padx=18, pady=10, command=addBusinessScreen)
    addBtn.bind("<Enter>", lambda e: addBtn.config(bg=PRIMARY, fg=addHoverFg))
    addBtn.bind("<Leave>", lambda e: addBtn.config(bg=TOOLBAR_BG, fg=addFg))
    addBtn.pack(side="left")

    sep2 = Label(toolbar, text="|", font=FONT_TB, fg=TEXT_LT, bg=TOOLBAR_BG, padx=4)
    sep2.pack(side="left")

    # My Businesses button
    myBizFg = "black"
    myBizHoverFg = "red"
    myBizBtn = Button(toolbar, text="🏢  My Businesses", font=FONT_TB,
                      bg=TOOLBAR_BG, fg=myBizFg, activebackground=PRIMARY,
                      activeforeground=myBizHoverFg, relief="flat", cursor="hand2",
                      bd=0, padx=18, pady=10, command=showOwnerBusinesses)
    myBizBtn.bind("<Enter>", lambda e: myBizBtn.config(bg=PRIMARY, fg=myBizHoverFg))
    myBizBtn.bind("<Leave>", lambda e: myBizBtn.config(bg=TOOLBAR_BG, fg=myBizFg))
    myBizBtn.pack(side="left")

    sep3 = Label(toolbar, text="|", font=FONT_TB, fg=TEXT_LT, bg=TOOLBAR_BG, padx=4)
    sep3.pack(side="left")


    # Log out on the right
    loFg = "black"
    loHoverFg = "red"
    loBtn = Button(toolbar, text="Log Out", font=FONT_TB,
                   bg=TOOLBAR_BG, fg=loFg, activebackground=ERROR_RED,
                   activeforeground=loHoverFg, relief="flat", cursor="hand2",
                   bd=0, padx=18, pady=10, command=logOut)
    loBtn.bind("<Enter>", lambda e: loBtn.config(bg=ERROR_RED, fg=loHoverFg))
    loBtn.bind("<Leave>", lambda e: loBtn.config(bg=TOOLBAR_BG, fg=loFg))
    loBtn.pack(side="right")

def showCustomerToolbar():
    """Show minimal toolbar for customers."""
    toolbar.pack(fill="x", side="top")
    for w in toolbar.winfo_children():
        w.destroy()
    loFg = "black"
    loHoverFg = "red"
    loBtn = Button(toolbar, text="Log Out", font=FONT_TB,
                   bg=TOOLBAR_BG, fg=loFg, activebackground=ERROR_RED,
                   activeforeground=loHoverFg, relief="flat", cursor="hand2",
                   bd=0, padx=18, pady=10, command=logOut)
    loBtn.bind("<Enter>", lambda e: loBtn.config(bg=ERROR_RED, fg=loHoverFg))
    loBtn.bind("<Leave>", lambda e: loBtn.config(bg=TOOLBAR_BG, fg=loFg))
    loBtn.pack(side="right")

def hideToolbar():
    """Unpack the toolbar and hide the header logout button (used on auth screen)."""
    toolbar.pack_forget()
    for w in toolbar.winfo_children():
        w.destroy()
    headerLogoutBtn.pack_forget()


def showProfile():
    """Show current user's profile screen."""
    global accountInUse
    clearScreen()
    user = accountDatabase.loc[accountInUse]
    # Coerce Saved to list in case CSV round-tripped it as a string
    saved = user["Saved"] if isinstance(user["Saved"], list) else []

    wrapper = Frame(mainContent, bg=BG)
    wrapper.pack(fill="both", expand=True)

    # Profile card
    card = Frame(wrapper, bg=CARD_BG, padx=48, pady=32,
                 highlightthickness=1, highlightbackground=BORDER)
    card.pack(pady=30)

    Label(card, text="👤", font=("Segoe UI", 36), fg=PRIMARY, bg=CARD_BG).pack()
    Label(card, text=str(user["Username"]), font=("Segoe UI", 18, "bold"), fg=TEXT_DK, bg=CARD_BG).pack(pady=(6, 2))
    Label(card, text=str(user["Email"]), font=FONT_BODY, fg=TEXT_MD, bg=CARD_BG).pack(pady=(0, 16))

    # Stats row
    statsF = Frame(card, bg=CARD_BG)
    statsF.pack(pady=(0, 16))
    for label, value in [
        ("Reviews Written", str(int(user["Number of Reviews"]))),
        ("Saved Businesses", str(len(saved))),
    ]:
        sc = Frame(statsF, bg="#f8fafc", highlightthickness=1, highlightbackground=BORDER, padx=24, pady=12)
        sc.pack(side="left", padx=8)
        Label(sc, text=value, font=("Segoe UI", 20, "bold"), fg=PRIMARY, bg="#f8fafc").pack()
        Label(sc, text=label, font=FONT_SMALL, fg=TEXT_MD, bg="#f8fafc").pack()

    # Recent reviews
    username = str(user["Username"])
    my_reviews = reviewsDatabase[reviewsDatabase["Username"] == username]
    if not my_reviews.empty:
        Label(card, text="Your Reviews", font=FONT_H2, fg=TEXT_DK, bg=CARD_BG, anchor="w").pack(fill="x", pady=(8, 6))
        for _, rev_row in my_reviews.tail(5).iterrows():
            rf = Frame(card, bg="#f8fafc", highlightthickness=1, highlightbackground=BORDER)
            rf.pack(fill="x", pady=3)
            stars_n = int(rev_row["Rating"]) if pd.notna(rev_row["Rating"]) else 0
            topRow = Frame(rf, bg="#f8fafc")
            topRow.pack(fill="x", padx=12, pady=(8, 2))
            avatarLbl = Label(topRow, text=username[0].upper(), font=("Segoe UI", 10, "bold"),
                              fg=WHITE, bg=getAvatarColor(username), width=2, padx=6, pady=4)
            avatarLbl.pack(side="left")
            Label(topRow, text=f"  {rev_row['Business Name']}", font=("Segoe UI", 10, "bold"), fg=TEXT_DK, bg="#f8fafc").pack(side="left")
            Label(rf, text=f"{'★'*stars_n}{'☆'*(5-stars_n)}", font=("Segoe UI", 11),
                  fg=STAR_GOLD, bg="#f8fafc", anchor="w", padx=12).pack(fill="x", pady=(0, 2))
            Label(rf, text=str(rev_row["Review"]), font=FONT_SMALL, fg=TEXT_DK, bg="#f8fafc",
                  anchor="w", wraplength=380, padx=12).pack(fill="x", pady=(0, 6))

    makeButton(card, "← Back to Home", setHomeScreen, style="ghost").pack(pady=(16, 0))

# AUTH SCREENS
def showAuthScreen():
    """Switch to the auth screen, hiding the toolbar and all other content."""
    hideToolbar()
    clearScreen()
    authWrapper.pack(fill="both", expand=True)
    flushLayout()

def resetAuthCardState():
    """Hide all auth-card input widgets so each flow can selectively repack them."""
    # Each auth sub-screen only repacks the widgets it needs, so everything
    # else must be hidden first to avoid stale widgets showing up.
    usernameInput.pack_forget()
    passwordInput.pack_forget()
    emailInput.pack_forget()
    startText.pack_forget()
    createNewAccountButton.pack_forget()
    loginButton.pack_forget()
    loginCompletedButton.pack_forget()
    createAccountCompletedButton.pack_forget()
    customerButton.pack_forget()
    ownerButton.pack_forget()

def showDefaultAuthScreen():
    """Show the landing auth card with just the Login and Create Account buttons."""
    showAuthScreen()
    resetAuthCardState()
    startText.config(text="")
    createNewAccountButton.pack(pady=(0, 8))
    loginButton.pack()

def loginScreen():
    """Show the username/password login form."""
    showAuthScreen()
    resetAuthCardState()
    usernameInput.pack(pady=(0, 8))
    passwordInput.pack(pady=(0, 8))
    loginCompletedButton.pack(pady=(4, 0))
    startText.pack(pady=(8, 0))

def newAccountScreen():
    """Show the registration form (username, email, password)."""
    showAuthScreen()
    resetAuthCardState()
    usernameInput.pack(pady=(0, 8))
    emailInput.pack(pady=(0, 8))
    passwordInput.pack(pady=(0, 8))
    createAccountCompletedButton.pack(pady=(4, 0))
    startText.pack(pady=(8, 0))

def login(username, password):
    """Validate credentials and navigate to the home screen on success."""
    index = accountDatabase.index[accountDatabase["Username"] == username].tolist()
    if not index:
        startText.config(text="Account Not Found", fg=ERROR_RED)
    elif accountDatabase.loc[index[0], "Password"] != password:
        startText.config(text="Incorrect Password", fg=ERROR_RED)
    else:
        global accountInUse
        accountInUse = index[0]  # store the DataFrame row index for the session
        setHomeScreen()

def createAccount(username, password, email, type):
    """Register a new account with the given type and navigate to home."""
    index = accountDatabase.index[accountDatabase["Username"] == username].tolist()
    if index:
        startText.config(text="Username is Unavailable", fg=ERROR_RED)
    else:
        global accountInUse
        # New row index is always len() before the append
        accountInUse = len(accountDatabase)
        # Column order must match: Username, Password, Email, NumReviews, Certificates, Reviews, Type, Businesses, Saved
        accountDatabase.loc[len(accountDatabase)] = [username, password, email, 0, [], [], type, [], []]
        saveData()
        setHomeScreen()

def accountType():
    """Validate registration fields, then show the account type selection step."""
    # All three fields must be filled before we ask what type of account they want
    if usernameInput.get() in ("Enter Username", ""):
        startText.config(text="Enter a valid username", fg=ERROR_RED)
    elif emailInput.get() in ("Enter Email", ""):
        startText.config(text="Enter a valid email", fg=ERROR_RED)
    elif passwordInput.get() in ("Enter Password", ""):
        startText.config(text="Enter a valid password", fg=ERROR_RED)
    else:
        showAuthScreen()
        resetAuthCardState()
        startText.config(text="I am a...", fg=TEXT_DK, font=FONT_H1, bg=CARD_BG)
        startText.pack(pady=(20, 12))
        customerButton.pack(pady=(0, 8))
        ownerButton.pack(pady=(0, 8))

def logOut():
    """Clear session state and return to the auth screen."""
    global accountInUse
    accountInUse = -1  # -1 means no session active
    # Manually restore placeholder text since the entry widgets persist across sessions
    usernameInput.delete(0, END); usernameInput.insert(0, "Enter Username"); usernameInput.config(fg="grey")
    passwordInput.delete(0, END); passwordInput.insert(0, "Enter Password"); passwordInput.config(fg="grey")
    emailInput.delete(0, END);    emailInput.insert(0, "Enter Email");       emailInput.config(fg="grey")
    headerLogoutBtn.pack_forget()
    showDefaultAuthScreen()

# BUSINESS FORM — Add
def uploadFile():
    """Open a file picker for the business image and store the path globally."""
    global filePath
    filePath = filedialog.askopenfilename()
    if filePath:
        businessImageInput.config(bg=SUCCESS, fg=WHITE if isDarkColor(SUCCESS) else TEXT_DK)
        createBusinessText.config(text="Image selected!", fg=SUCCESS)
        if imageCheckLabel:
            imageCheckLabel.config(text="✓")  # visual confirmation checkmark
    else:
        createBusinessText.config(text="No file selected", fg=ERROR_RED)

def uploadLicense():
    """Open a file picker for the business license document and store the path."""
    global licensePath
    licensePath = filedialog.askopenfilename(
        title="Select Business License",
        filetypes=[("Documents & Images", "*.pdf *.png *.jpg *.jpeg"), ("All files", "*.*")]
    )
    if licensePath:
        licenseUploadBtn.config(bg=SUCCESS, fg=WHITE)
        createBusinessText.config(text="License uploaded!", fg=SUCCESS)
        if licenseCheckLabel:
            licenseCheckLabel.config(text="✓")  # visual confirmation checkmark
    else:
        createBusinessText.config(text="No license selected", fg=ERROR_RED)

def addBusinessScreen():
    """Show the form for adding a new business listing."""
    global businessNameInput, businessLocationInput, businessDescriptionInput, licenseUploadBtn
    global selectedCategory, businessCategoryInput
    global businessImageInput, createBusinessButton, createBusinessText
    global imageCheckLabel, licenseCheckLabel
    clearScreen()

    # Centered card wrapper
    wrapper = Frame(mainContent, bg=BG)
    wrapper.pack(fill="both", expand=True)
    card = Frame(wrapper, bg=CARD_BG, padx=48, pady=36,
                 highlightthickness=1, highlightbackground=BORDER)
    card.pack(pady=40)

    Label(card, text="Create Your Business", font=FONT_H1, fg=TEXT_DK, bg=CARD_BG).pack(pady=(0, 4))
    Label(card, text="Fill in the details below to list your business", font=FONT_SMALL, fg=TEXT_MD, bg=CARD_BG).pack(pady=(0, 20))

    createBusinessTitle.pack_forget()
    businessNameInput = makeEntry(card, width=36)
    addPlaceholder(businessNameInput, "Business Name")

    selectedCategory = StringVar()
    businessCategoryInput = ttk.Combobox(card,
        values=["Food","Service","Retail","Health & Wellness","Education",
                "Automotive","Travel & Hospitality","Entertainment","Home Services"],
        textvariable=selectedCategory, state="readonly", width=34, font=FONT_BODY)
    businessCategoryInput.set("Select Category")

    businessLocationInput = makeEntry(card, width=36)
    addPlaceholder(businessLocationInput, "Business Location")

    businessDescriptionInput = makeEntry(card, width=36)
    addPlaceholder(businessDescriptionInput, "Business Description")

    createBusinessButton = makeButton(
        card,
        "Create Business",
        lambda: createBusiness(
            businessNameInput.get(),
            businessLocationInput.get(),
            businessDescriptionInput.get()
        ),
        style="primary"
    )

    createBusinessText = Label(card, text="", font=FONT_BODY, fg=ERROR_RED, bg=CARD_BG)

    businessNameInput.pack(pady=(0, 8), fill="x")
    businessCategoryInput.pack(pady=(0, 8), fill="x")
    businessLocationInput.pack(pady=(0, 8), fill="x")
    businessDescriptionInput.pack(pady=(0, 8), fill="x")

    # Image upload row with checkmark
    imgRow = Frame(card, bg=CARD_BG)
    imgRow.pack(pady=(0, 8), fill="x")
    businessImageInput = makeButton(imgRow, "🖼  Upload Business Image", uploadFile, style="ghost")
    businessImageInput.config(bg="#eff6ff", fg=WHITE if isDarkColor("#eff6ff") else TEXT_DK)
    businessImageInput.pack(side="left", fill="x", expand=True)
    imageCheckLabel = Label(imgRow, text="", font=("Segoe UI", 14, "bold"), fg=SUCCESS, bg=CARD_BG, width=2)
    imageCheckLabel.pack(side="left", padx=(8, 0))

    # License upload row with checkmark
    licRow = Frame(card, bg=CARD_BG)
    licRow.pack(pady=(0, 8), fill="x")
    licenseUploadBtn = makeButton(licRow, "📄  Upload Business License", uploadLicense, style="ghost")
    licenseUploadBtn.pack(side="left", fill="x", expand=True)
    licenseCheckLabel = Label(licRow, text="", font=("Segoe UI", 14, "bold"), fg=SUCCESS, bg=CARD_BG, width=2)
    licenseCheckLabel.pack(side="left", padx=(8, 0))

    createBusinessButton.pack(pady=(12, 4), fill="x")
    createBusinessText.pack(pady=(4, 0))
    flushLayout()

def createBusiness(name, location, description):
    """Validate the new business form and append it to the database."""
    global filePath, licensePath, accountInUse
    clean_name = str(name).strip()
    # Validate all required fields before writing to the database
    if businessNameExists(clean_name):                createBusinessText.config(text="Business name already exists", fg=ERROR_RED)
    elif businessNameInput.get() == "Business Name":  createBusinessText.config(text="Enter valid name", fg=ERROR_RED)
    elif businessLocationInput.get() == "Business Location": createBusinessText.config(text="Enter valid location", fg=ERROR_RED)
    elif selectedCategory.get() == "Select Category": createBusinessText.config(text="Select a category", fg=ERROR_RED)
    elif businessDescriptionInput.get() == "Business Description": createBusinessText.config(text="Enter valid description", fg=ERROR_RED)
    elif not filePath:                                createBusinessText.config(text="Upload a business image", fg=ERROR_RED)
    elif not licensePath:                             createBusinessText.config(text="Upload a business license", fg=ERROR_RED)
    else:
        # DateAdded is stored as ISO string so sorting/comparison stays simple
        businessDatabase.loc[len(businessDatabase)] = [clean_name, location, filePath, description, selectedCategory.get(), 0.0, 0, 0, [], licensePath, datetime.date.today().isoformat()]
        # Ensure the owner's Businesses column is a list before appending
        if not isinstance(accountDatabase.at[accountInUse, "Businesses"], list):
            accountDatabase.at[accountInUse, "Businesses"] = []
        accountDatabase.at[accountInUse, "Businesses"].append(clean_name)
        saveData()
        filePath = ""    # reset so next creation starts fresh
        licensePath = ""
        setHomeScreen()

# BUSINESS FORM — Edit
def updateBusiness(updatedValue, type, index):
    """Write a single field update into the business DataFrame at the given row index."""
    if type == "Name":        businessDatabase.loc[index, "Name"] = updatedValue
    if type == "Location":    businessDatabase.loc[index, "Location"] = updatedValue
    if type == "Description": businessDatabase.loc[index, "Description"] = updatedValue
    if type == "Category":    businessDatabase.loc[index, "Category"] = updatedValue
    if type == "Image":       businessDatabase.loc[index, "Image"] = updatedValue

def editBusiness(item):
    """Show the edit form pre-populated with the given business's current data."""
    global currentBusinessIndex
    global editBusinessNameInput, editBusinessLocationInput, editBusinessDescriptionInput
    global editSelectedCategory, editBusinessCategoryInput, editBusinessImageInput, editBusinessButton
    clearScreen()
    indexlist = businessDatabase.index[businessDatabase["Name"] == item].tolist()
    if not indexlist: return  # business may have been deleted between clicks
    currentBusinessIndex = indexlist[0]

    # Centered card wrapper
    wrapper = Frame(mainContent, bg=BG)
    wrapper.pack(fill="both", expand=True)
    card = Frame(wrapper, bg=CARD_BG, padx=48, pady=36,
                 highlightthickness=1, highlightbackground=BORDER)
    card.pack(pady=40)

    Label(card, text="Edit Business", font=FONT_H1, fg=TEXT_DK, bg=CARD_BG).pack(pady=(0, 4))
    Label(card, text=f"Editing: {item}", font=FONT_SMALL, fg=TEXT_MD, bg=CARD_BG).pack(pady=(0, 20))

    editBusinessTitle.pack_forget()

    editBusinessNameInput = makeEntry(card, width=36)
    editBusinessNameInput.insert(0, businessDatabase.loc[currentBusinessIndex, "Name"])

    editBusinessLocationInput = makeEntry(card, width=36)
    editBusinessLocationInput.insert(0, businessDatabase.loc[currentBusinessIndex, "Location"])

    editSelectedCategory = StringVar()
    editBusinessCategoryInput = ttk.Combobox(card,
        values=["Food","Service","Retail","Health & Wellness","Education",
                "Automotive","Travel & Hospitality","Entertainment","Home Services"],
        textvariable=editSelectedCategory, state="readonly", width=34, font=FONT_BODY)
    editSelectedCategory.set(businessDatabase.loc[currentBusinessIndex, "Category"])

    editBusinessDescriptionInput = makeEntry(card, width=36)
    editBusinessDescriptionInput.insert(0, businessDatabase.loc[currentBusinessIndex, "Description"])

    editBusinessImageInput = makeButton(card, "Upload New Image", uploadFile, style="ghost")
    editBusinessButton = makeButton(card, "Save Changes", finalizeEdits, style="success")

    editBusinessNameInput.pack(pady=(0, 8), fill="x")
    editBusinessLocationInput.pack(pady=(0, 8), fill="x")
    editBusinessCategoryInput.pack(pady=(0, 8), fill="x")
    editBusinessDescriptionInput.pack(pady=(0, 8), fill="x")
    editBusinessImageInput.pack(pady=(0, 8), fill="x")
    editBusinessButton.pack(pady=(12, 4), fill="x")
    flushLayout()

def finalizeEdits():
    """Save all edits from the edit form and cascade any name change to related tables."""
    global currentBusinessIndex, filePath, reviewsDatabase
    index = currentBusinessIndex
    if index < 0 or index not in businessDatabase.index:
        return
    old_name = str(businessDatabase.loc[index, "Name"])
    new_name_input = str(editBusinessNameInput.get()).strip()
    if new_name_input in ("", "Business Name"):
        return
    # exclude_index prevents the current business from blocking its own name save
    if businessNameExists(new_name_input, exclude_index=index):
        messagebox.showerror("Duplicate Name", "A business with this name already exists.")
        return
    updateBusiness(new_name_input, "Name", index)
    # Only update fields that were actually changed (not left at placeholder text)
    if editBusinessLocationInput.get() not in ("", "Business Location"): updateBusiness(editBusinessLocationInput.get(), "Location", index)
    if editBusinessDescriptionInput.get() not in ("", "Business Description"): updateBusiness(editBusinessDescriptionInput.get(), "Description", index)
    if editSelectedCategory.get() != "Select Category":                  updateBusiness(editSelectedCategory.get(), "Category", index)
    if filePath:
        updateBusiness(filePath, "Image", index)
        filePath = ""
    new_name = str(businessDatabase.loc[index, "Name"])
    if new_name != old_name:
        # Cascade rename to owner account lists and all historical reviews
        for acc_idx in accountDatabase.index:
            businesses = accountDatabase.loc[acc_idx, "Businesses"]
            if isinstance(businesses, list):
                accountDatabase.at[acc_idx, "Businesses"] = [new_name if b == old_name else b for b in businesses]
        if "Business Name" in reviewsDatabase.columns:
            reviewsDatabase.loc[reviewsDatabase["Business Name"] == old_name, "Business Name"] = new_name
    refreshBusinessReviewsFromTable()
    saveData()
    setHomeScreen()

def deleteBusiness(item):
    """Delete a business listing and all its associated reviews after confirmation."""
    global reviewsDatabase
    if not messagebox.askyesno("Delete Business", f"Delete '{item}'? This will remove its reviews too."):
        return
    indexlist = businessDatabase.index[businessDatabase["Name"] == item].tolist()
    if indexlist:
        businessDatabase.drop(index=indexlist[0], inplace=True)
        businessDatabase.reset_index(drop=True, inplace=True)  # keeps index contiguous
    # Remove from every owner's Businesses list so it doesn't show as orphaned
    for acc_idx in accountDatabase.index:
        businesses = accountDatabase.loc[acc_idx, "Businesses"]
        if isinstance(businesses, list):
            accountDatabase.at[acc_idx, "Businesses"] = [b for b in businesses if b != item]
    # Purge all reviews for this business from the reviews table
    if "Business Name" in reviewsDatabase.columns:
        reviewsDatabase = reviewsDatabase[reviewsDatabase["Business Name"] != item].reset_index(drop=True)
    refreshBusinessReviewsFromTable()
    saveData()
    showOwnerBusinesses()

# OWNER — My Businesses screen
def replyToReview(rev_idx, refresh_callback):
    """Open a dialog for the owner to type or edit a reply to a review."""
    existing = ""
    if rev_idx in reviewsDatabase.index:
        val = reviewsDatabase.at[rev_idx, "Reply"]
        existing = str(val).strip() if pd.notna(val) else ""
        if existing == "nan":
            existing = ""

    win = Toplevel(startScreen)
    win.title("Owner Reply")
    win.configure(bg=BG)
    win.geometry("440x280")
    win.resizable(False, False)
    win.grab_set()

    hdr = Frame(win, bg=HEADER_BG)
    hdr.pack(fill="x")
    Label(hdr, text="Reply to Review", font=FONT_H1, fg=WHITE, bg=HEADER_BG, pady=12, padx=20).pack(anchor="w")

    body = Frame(win, bg=BG, padx=24, pady=16)
    body.pack(fill="both", expand=True)
    Label(body, text="Your public reply:", font=FONT_BODY, fg=TEXT_DK, bg=BG).pack(anchor="w", pady=(0, 6))

    replyText = Text(body, height=5, width=44, wrap="word",
                     font=FONT_BODY, fg=TEXT_DK, bg=INPUT_BG,
                     insertbackground=TEXT_DK, relief="flat",
                     highlightthickness=1, highlightbackground=INPUT_BD,
                     highlightcolor=PRIMARY, bd=0, padx=8, pady=6)
    replyText.pack(fill="x")
    if existing:
        replyText.insert("1.0", existing)

    def submitReply():
        text = replyText.get("1.0", "end-1c").strip()
        reviewsDatabase.at[rev_idx, "Reply"] = text
        saveData()
        win.destroy()
        refresh_callback()

    makeButton(body, "Save Reply", submitReply, style="primary").pack(pady=(12, 0), anchor="e")


def _buildReviewsPopup(body, biz_name, refresh):
    """Build review list inside the owner review popup."""
    idxlist = businessDatabase.index[businessDatabase["Name"] == biz_name].tolist()
    if not idxlist:
        return
    row = businessDatabase.loc[idxlist[0]]
    subset = reviewsDatabase[reviewsDatabase["Business Name"] == biz_name]

    if row["Number of Reviews"] > 0:
        s = starsStr(row["Rating"], row["Number of Reviews"])
        Label(body, text=f"{s}  {round(row['Rating'], 1)}/5  ({int(row['Number of Reviews'])} reviews)",
              font=("Segoe UI", 13), fg=STAR_GOLD, bg=CARD_BG).pack(anchor="w", pady=(0, 12))
    else:
        Label(body, text="No reviews yet.", font=FONT_BODY, fg=TEXT_DK, bg=CARD_BG).pack(anchor="w", pady=(0, 12))
        return

    outer = Frame(body, bg=CARD_BG)
    outer.pack(fill="both", expand=True)
    canvas = Canvas(outer, bg=CARD_BG, highlightthickness=0)
    sb = Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    inner = Frame(canvas, bg=CARD_BG)
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.bind("<Enter>", lambda e, c=canvas: setActiveScrollCanvas(c))
    canvas.bind("<Leave>", lambda e: setActiveScrollCanvas(None))

    # Only show the Reply button to owners, not to customers
    is_owner = accountInUse >= 0 and accountDatabase.loc[accountInUse, "Type"] == "Owner"

    for rev_idx, rev_row in subset.iterrows():
        rc = Frame(inner, bg="#f8fafc", highlightthickness=1, highlightbackground=BORDER)
        rc.pack(fill="x", pady=4, padx=2)
        stars_n = int(rev_row["Rating"]) if pd.notna(rev_row["Rating"]) else 0
        # Fall back to "Anonymous" if the username was never stored
        user = str(rev_row["Username"]) if str(rev_row["Username"]) not in ("", "nan") else "Anonymous"
        topRow = Frame(rc, bg="#f8fafc")
        topRow.pack(fill="x", padx=12, pady=(8, 2))
        avatarLbl = Label(topRow, text=user[0].upper(), font=("Segoe UI", 10, "bold"),
                          fg=WHITE, bg=getAvatarColor(user), width=2, padx=6, pady=4)
        avatarLbl.pack(side="left")
        Label(topRow, text=f"  {user}", font=("Segoe UI", 10, "bold"), fg=TEXT_DK, bg="#f8fafc").pack(side="left")
        Label(rc, text=f"{'★'*stars_n}{'☆'*(5-stars_n)}", font=("Segoe UI", 11),
              fg=STAR_GOLD, bg="#f8fafc", anchor="w", padx=12).pack(fill="x", pady=(0, 2))
        Label(rc, text=str(rev_row["Review"]), font=FONT_BODY, fg=TEXT_DK, bg="#f8fafc",
              anchor="w", wraplength=460, justify="left", padx=12).pack(fill="x", pady=(0, 6))

        reply_val = rev_row["Reply"] if "Reply" in rev_row.index else ""
        reply = "" if pd.isna(reply_val) else str(reply_val).strip()
        if reply and reply != "nan":
            replyF = Frame(rc, bg="#eff6ff", padx=12, pady=6)
            replyF.pack(fill="x", padx=8, pady=(0, 8))
            Label(replyF, text="💬 Owner Reply:", font=("Segoe UI", 9, "bold"),
                  fg=PRIMARY, bg="#eff6ff", anchor="w").pack(fill="x")
            Label(replyF, text=reply, font=FONT_SMALL, fg=TEXT_DK, bg="#eff6ff",
                  anchor="w", wraplength=420, justify="left").pack(fill="x")

        if is_owner:
            # Label changes to "Edit Reply" once a reply has been saved
            btn_text = "Edit Reply" if (reply and reply != "nan") else "💬 Reply"
            btnRow = Frame(rc, bg="#f8fafc")
            btnRow.pack(fill="x", padx=12, pady=(0, 8))
            makeButton(btnRow, btn_text,
                       lambda ri=rev_idx: replyToReview(ri, refresh),
                       style="ghost").pack(side="right")

    inner.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))


def viewBusinessReviews(biz_name):
    """Open a popup showing all reviews for a business the owner owns."""
    win = Toplevel(startScreen)
    win.title(f"Reviews — {biz_name}")
    win.configure(bg=BG)
    win.geometry("580x560")
    win.grab_set()

    hdr = Frame(win, bg=HEADER_BG)
    hdr.pack(fill="x")
    Label(hdr, text=f"Reviews: {biz_name}", font=FONT_H1,
          fg=WHITE, bg=HEADER_BG, pady=14, padx=20).pack(anchor="w")

    body = Frame(win, bg=CARD_BG, padx=24, pady=16)
    body.pack(fill="both", expand=True)

    foot = Frame(win, bg=CARD_BG, padx=24, pady=10)
    foot.pack(fill="x")
    makeButton(foot, "Close", win.destroy, style="ghost").pack(anchor="e")

    def refresh():
        for w in body.winfo_children():
            w.destroy()
        _buildReviewsPopup(body, biz_name, refresh)

    refresh()


def showOwnerBusinesses():
    """Show the owner's business management screen."""
    clearScreen()
    global accountInUse
    businesses = accountDatabase.loc[accountInUse, "Businesses"]
    if not isinstance(businesses, list):
        businesses = []

    # Page title
    hdrF = Frame(mainContent, bg=BG)
    hdrF.pack(fill="x", padx=20, pady=(20, 4))
    Label(hdrF, text="My Businesses", font=("Segoe UI", 18, "bold"), fg=TEXT_DK, bg=BG).pack(side="left")
    makeButton(hdrF, "＋  Add Business", addBusinessScreen, style="primary").pack(side="right")

    # Scrollable list
    containerF = Frame(mainContent, bg=BG)
    containerF.pack(fill="both", expand=True)

    canvas = Canvas(containerF, bg=BG, highlightthickness=0)
    sb = Scrollbar(containerF, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    canvas.bind("<Enter>", lambda e, c=canvas: setActiveScrollCanvas(c))
    canvas.bind("<Leave>", lambda e: setActiveScrollCanvas(None))
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    listFrame = Frame(canvas, bg=BG)
    canvas.create_window((0, 0), window=listFrame, anchor="nw")
    listFrame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    if not businesses:
        Label(listFrame, text="You haven't added any businesses yet.",
              font=FONT_H2, fg=TEXT_MD, bg=BG, pady=60).pack()
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        flushLayout()
        return

    canvas.update_idletasks()
    available_width = max(canvas.winfo_width(), 1)
    min_card_width = 480  # cards below this width look cramped
    columns = max(1, available_width // min_card_width)
    for c in range(columns):
        # "uniform" ensures all columns get equal width regardless of content
        listFrame.grid_columnconfigure(c, weight=1, uniform="owner_cards")
    card_index = 0
    for biz_name in businesses:
        indexlist = businessDatabase.index[businessDatabase["Name"] == biz_name].tolist()
        if not indexlist:
            continue
        row = businessDatabase.loc[indexlist[0]]
        grid_row = card_index // columns
        grid_col = card_index % columns

        shadowF = Frame(listFrame, bg=SHADOW)
        shadowF.grid(row=grid_row, column=grid_col, padx=10, pady=8, sticky="nsew")
        card = Frame(shadowF, bg=CARD_BG)
        card.pack(padx=1, pady=1, fill="x")

        # Image
        imgF = Frame(card, bg="#f1f5f9", width=108, height=108)
        imgF.pack(side="left", padx=14, pady=14)
        imgF.pack_propagate(False)  # lock the image frame to its fixed 108x108 size
        try:
            photo = loadCardPhoto(row["Image"])
            lbl = Label(imgF, image=photo, bg=CARD_BG)
            lbl.image = photo  # hold a reference so GC doesn't discard the image
            lbl.pack(expand=True)
        except Exception as e:
            logImageFailure(row["Image"], e)
            Label(imgF, text="🏢", font=("Segoe UI", 30), bg="#f1f5f9", fg=TEXT_LT).pack(expand=True, fill="both")

        # Info
        infoF = Frame(card, bg=CARD_BG)
        infoF.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=14)
        nameRow = Frame(infoF, bg=CARD_BG)
        nameRow.pack(fill="x")
        Label(nameRow, text=row["Name"], font=("Segoe UI", 14, "bold"), fg=TEXT_DK, bg=CARD_BG, anchor="w").pack(side="left")
        if isVerified(row):
            Label(nameRow, text=" ✅", font=("Segoe UI", 11), fg=SUCCESS, bg=CARD_BG).pack(side="left")
        cat_color = getCategoryColor(row["Category"])
        Label(infoF, text=f"  {row['Category']}  ", font=("Segoe UI", 9, "bold"),
              fg=WHITE, bg=cat_color, padx=4, pady=3).pack(anchor="w", pady=(5, 3))
        Label(infoF, text="📍 " + str(row["Location"]), font=("Segoe UI", 10), fg=TEXT_MD, bg=CARD_BG, anchor="w").pack(fill="x")
        if row["Number of Reviews"] > 0:
            makeStarRow(infoF, CARD_BG, float(row["Rating"]), int(row["Number of Reviews"]))
        else:
            Label(infoF, text="No reviews yet", font=("Segoe UI", 10, "italic"), fg=TEXT_LT, bg=CARD_BG, anchor="w").pack(fill="x", pady=(4, 0))

        # Action buttons
        btnF = Frame(card, bg=CARD_BG)
        btnF.pack(side="right", padx=20, pady=14)
        editBtn = makeButton(btnF, "Edit", lambda b=biz_name: editBusiness(b), style="primary")
        editBtn.config(fg="black", activeforeground="red")
        editBtn.bind("<Enter>", lambda e, b=editBtn: b.config(bg=PRIMARY_DK, fg="red"))
        editBtn.bind("<Leave>", lambda e, b=editBtn: b.config(bg=PRIMARY, fg="black"))
        editBtn.pack(pady=(0, 6), fill="x")
        makeButton(btnF, "View Reviews", lambda b=biz_name: viewBusinessReviews(b), style="ghost").pack(pady=(0, 6), fill="x")
        deleteBtn = makeButton(btnF, "Delete", lambda b=biz_name: deleteBusiness(b), style="danger")
        deleteBtn.config(fg="black", activeforeground="red")
        deleteBtn.bind("<Enter>", lambda e, b=deleteBtn: b.config(bg="#b91c1c", fg="red"))
        deleteBtn.bind("<Leave>", lambda e, b=deleteBtn: b.config(bg=ERROR_RED, fg="black"))
        deleteBtn.pack(fill="x")
        card_index += 1
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    flushLayout()


def showAnalytics():
    """Show the analytics dashboard with aggregate stats for the owner's businesses."""
    global accountInUse
    clearScreen()
    businesses = accountDatabase.loc[accountInUse, "Businesses"]
    # Coerce to list in case CSV stored the Businesses column as a string
    if not isinstance(businesses, list):
        businesses = []

    hdrF = Frame(mainContent, bg=BG)
    hdrF.pack(fill="x", padx=20, pady=(20, 4))
    Label(hdrF, text="📊 Analytics Dashboard", font=("Segoe UI", 18, "bold"), fg=TEXT_DK, bg=BG).pack(side="left")

    # Compute weighted average rating across all of the owner's businesses
    total_reviews = 0
    total_rating_sum = 0.0
    for biz_name in businesses:
        idxlist = businessDatabase.index[businessDatabase["Name"] == biz_name].tolist()
        if idxlist:
            r = businessDatabase.loc[idxlist[0]]
            nr = int(r["Number of Reviews"]) if pd.notna(r["Number of Reviews"]) else 0
            total_reviews += nr
            total_rating_sum += (float(r["Rating"]) * nr) if pd.notna(r["Rating"]) else 0.0
    overall_avg = (total_rating_sum / total_reviews) if total_reviews > 0 else 0.0

    statsF = Frame(mainContent, bg=BG)
    statsF.pack(fill="x", padx=20, pady=(8, 16))
    for label, value in [
        ("Businesses", str(len(businesses))),
        ("Total Reviews", str(total_reviews)),
        ("Avg Rating", f"{overall_avg:.1f} / 5"),
    ]:
        sc = Frame(statsF, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER, padx=28, pady=14)
        sc.pack(side="left", padx=(0, 12), pady=4)
        Frame(sc, bg=PRIMARY, height=3).pack(fill="x", pady=(0, 10))
        Label(sc, text=value, font=("Segoe UI", 22, "bold"), fg=PRIMARY, bg=CARD_BG).pack()
        Label(sc, text=label, font=FONT_SMALL, fg=TEXT_MD, bg=CARD_BG).pack()

    if not businesses:
        Label(mainContent, text="Add a business to see analytics.",
              font=FONT_H2, fg=TEXT_MD, bg=BG, pady=40).pack()
        return

    Label(mainContent, text="Per-Business Breakdown", font=FONT_H2, fg=TEXT_DK, bg=BG, anchor="w").pack(fill="x", padx=24, pady=(0, 8))

    containerF = Frame(mainContent, bg=BG)
    containerF.pack(fill="both", expand=True)
    canvas = Canvas(containerF, bg=BG, highlightthickness=0)
    sb = Scrollbar(containerF, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    canvas.bind("<Enter>", lambda e, c=canvas: setActiveScrollCanvas(c))
    canvas.bind("<Leave>", lambda e: setActiveScrollCanvas(None))
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    listFrame = Frame(canvas, bg=BG)
    canvas.create_window((0, 0), window=listFrame, anchor="nw")
    listFrame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    for biz_name in businesses:
        idxlist = businessDatabase.index[businessDatabase["Name"] == biz_name].tolist()
        if not idxlist:
            continue
        row = businessDatabase.loc[idxlist[0]]
        num_reviews = int(row["Number of Reviews"]) if pd.notna(row["Number of Reviews"]) else 0
        avg_rating = float(row["Rating"]) if pd.notna(row["Rating"]) else 0.0

        subset = reviewsDatabase[reviewsDatabase["Business Name"] == biz_name]
        # Build a 1–5 star frequency histogram for the bar chart
        star_counts = {i: 0 for i in range(1, 6)}
        for rv in pd.to_numeric(subset["Rating"], errors="coerce").fillna(0).tolist():
            rv_int = int(rv)
            if 1 <= rv_int <= 5:
                star_counts[rv_int] += 1

        cardOuter = Frame(listFrame, bg=BORDER)
        cardOuter.pack(padx=16, pady=6, fill="x")
        card = Frame(cardOuter, bg=CARD_BG, padx=20, pady=14)
        card.pack(padx=1, pady=1, fill="x")

        topF = Frame(card, bg=CARD_BG)
        topF.pack(fill="x", pady=(0, 8))
        Label(topF, text=row["Name"], font=FONT_CARD, fg=TEXT_DK, bg=CARD_BG).pack(side="left")
        if num_reviews > 0:
            s = starsStr(avg_rating, num_reviews)
            Label(topF, text=f"  {s}  {avg_rating:.1f}/5  ({num_reviews} reviews)",
                  font=("Segoe UI", 10), fg=STAR_GOLD, bg=CARD_BG).pack(side="left", padx=(8, 0))
        else:
            Label(topF, text="  No reviews yet", font=FONT_SMALL, fg=TEXT_LT, bg=CARD_BG).pack(side="left", padx=(8, 0))

        if num_reviews > 0:
            for star in range(5, 0, -1):  # render 5-star row first, then 4, 3, …
                count = star_counts[star]
                pct = count / num_reviews
                barF = Frame(card, bg=CARD_BG)
                barF.pack(fill="x", pady=1)
                Label(barF, text="★" * star, font=("Segoe UI", 9), fg=STAR_GOLD, bg=CARD_BG,
                      width=6, anchor="e").pack(side="left")
                barBg = Frame(barF, bg=BORDER, height=14, width=200)
                barBg.pack(side="left", padx=(6, 6))
                barBg.pack_propagate(False)  # lock bar background to fixed 200px width
                if count > 0:
                    # min width of 2px so even a single review shows a visible sliver
                    Frame(barBg, bg=STAR_GOLD, width=max(2, int(200 * pct)), height=14).place(x=0, y=0)
                Label(barF, text=str(count), font=("Segoe UI", 9), fg=TEXT_MD, bg=CARD_BG,
                      width=3, anchor="w").pack(side="left")

    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    flushLayout()


def isSaved(biz_name):
    """Return True if the current user has bookmarked the given business."""
    global accountInUse
    if accountInUse < 0:  # no session; can't have saved anything
        return False
    saved = accountDatabase.loc[accountInUse, "Saved"]
    return isinstance(saved, list) and biz_name in saved

def toggleSave(biz_name, btn):
    """Add or remove a business from the current user's saved list and update the button."""
    global accountInUse
    if accountInUse < 0:
        return
    saved = accountDatabase.loc[accountInUse, "Saved"]
    # Coerce to list in case CSV loaded it as a string
    if not isinstance(saved, list):
        accountDatabase.at[accountInUse, "Saved"] = []
        saved = accountDatabase.loc[accountInUse, "Saved"]
    if biz_name in saved:
        saved.remove(biz_name)
        btn.config(text="🔖 Save", fg=PRIMARY)
    else:
        saved.append(biz_name)
        btn.config(text="🔖 Saved", fg=PRIMARY)
    accountDatabase.at[accountInUse, "Saved"] = saved
    saveData()

def showSavedBusinesses():
    """Display a scrollable list of the current user's bookmarked businesses."""
    global accountInUse
    clearScreen()
    hdrF = Frame(mainContent, bg=BG)
    hdrF.pack(fill="x", padx=20, pady=(20, 4))
    Label(hdrF, text="Saved Businesses", font=("Segoe UI", 18, "bold"), fg=TEXT_DK, bg=BG).pack(side="left")
    makeButton(hdrF, "← Back", setHomeScreen, style="ghost").pack(side="right")

    saved = accountDatabase.loc[accountInUse, "Saved"] if accountInUse >= 0 else []
    # Coerce in case the column was serialized as a string in the CSV
    if not isinstance(saved, list):
        saved = []

    containerF = Frame(mainContent, bg=BG)
    containerF.pack(fill="both", expand=True)
    canvas = Canvas(containerF, bg=BG, highlightthickness=0)
    sb = Scrollbar(containerF, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    canvas.bind("<Enter>", lambda e, c=canvas: setActiveScrollCanvas(c))
    canvas.bind("<Leave>", lambda e: setActiveScrollCanvas(None))
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    listFrame = Frame(canvas, bg=BG)
    canvas.create_window((0, 0), window=listFrame, anchor="nw")
    listFrame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    if not saved:
        Label(listFrame, text="No saved businesses yet. Bookmark businesses using the 🔖 button.",
              font=FONT_H2, fg=TEXT_MD, bg=BG, pady=60, wraplength=500).pack()
        return

    shown = 0
    for biz_name in saved:
        indexlist = businessDatabase.index[businessDatabase["Name"] == biz_name].tolist()
        if not indexlist:
            continue
        row = businessDatabase.loc[indexlist[0]]
        shadowF = Frame(listFrame, bg=SHADOW)
        shadowF.pack(padx=16, pady=6, fill="x")
        card = Frame(shadowF, bg=CARD_BG)
        card.pack(padx=1, pady=1, fill="x")

        imgF = Frame(card, bg="#f1f5f9", width=108, height=108)
        imgF.pack(side="left", padx=14, pady=14)
        imgF.pack_propagate(False)
        try:
            photo = loadCardPhoto(row["Image"])
            lbl = Label(imgF, image=photo, bg=CARD_BG)
            lbl.image = photo
            lbl.pack(expand=True)
        except:
            Label(imgF, text="🏢", font=("Segoe UI", 30), bg="#f1f5f9", fg=TEXT_LT).pack(expand=True, fill="both")

        infoF = Frame(card, bg=CARD_BG)
        infoF.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=14)
        nameRow = Frame(infoF, bg=CARD_BG)
        nameRow.pack(fill="x")
        Label(nameRow, text=row["Name"], font=("Segoe UI", 14, "bold"), fg=TEXT_DK, bg=CARD_BG, anchor="w").pack(side="left")
        if isVerified(row):
            Label(nameRow, text=" ✅", font=("Segoe UI", 11), fg=SUCCESS, bg=CARD_BG).pack(side="left")
        cat_color = getCategoryColor(row["Category"])
        Label(infoF, text=f"  {row['Category']}  ", font=("Segoe UI", 9, "bold"),
              fg=WHITE, bg=cat_color, padx=4, pady=3).pack(anchor="w", pady=(5, 3))
        Label(infoF, text="📍 " + str(row["Location"]), font=("Segoe UI", 10), fg=TEXT_MD, bg=CARD_BG, anchor="w").pack(fill="x")
        if row["Number of Reviews"] > 0:
            makeStarRow(infoF, CARD_BG, float(row["Rating"]), int(row["Number of Reviews"]))
        else:
            Label(infoF, text="Be the first to review!", font=("Segoe UI", 10, "italic"), fg=TEXT_LT, bg=CARD_BG, anchor="w").pack(fill="x", pady=(4, 0))

        btnF = Frame(card, bg=CARD_BG)
        btnF.pack(side="right", padx=24, pady=18)
        makeButton(btnF, "View Details", lambda r=row: showDetails(r), style="primary").pack(pady=(0, 10), fill="x")
        saveBtn = Button(btnF, text="🔖 Remove", font=FONT_BTN,
                         bg="#fee2e2", fg=ERROR_RED, activebackground="#fecaca",
                         activeforeground=ERROR_RED, relief="flat", cursor="hand2", bd=0, padx=16, pady=8)
        saveBtn.config(command=lambda b=biz_name, s=saveBtn: [toggleSave(b, s), showSavedBusinesses()])
        saveBtn.pack(fill="x")
        shown += 1

    if shown == 0:
        Label(listFrame, text="None of your saved businesses exist anymore.",
              font=FONT_H2, fg=TEXT_MD, bg=BG, pady=60).pack()

# CANVAS SCROLL
def on_frame_configure(event):
    """Update the businessViewer scroll region when the inner frame resizes."""
    businessViewer.configure(scrollregion=businessViewer.bbox("all"))

# BUSINESS CARDS
def starsStr(r, count):
    """Return a 5-character star string representing the rounded average rating."""
    filled = round(r)
    return "★" * filled + "☆" * (5 - filled)

def _setBg(widget, color):
    """Recursively set bg on all non-Button widgets that use a card color."""
    try:
        if isinstance(widget, Button): return  # buttons manage their own hover color
        # Only recolor widgets already using a card background to avoid clobbering others
        if str(widget.cget("bg")) in (CARD_BG, CARD_HOVER):
            widget.config(bg=color)
        for child in widget.winfo_children():
            _setBg(child, color)
    except: pass

def loadBusinessImage(source):
    """Load a PIL Image from a local path or a remote URL.

    Remote images use a browser User-Agent header because some hosts block
    Python's default urllib agent. If macOS certificate verification fails,
    we fall back to an unverified SSL context rather than crashing.
    """
    if isinstance(source, str) and source.lower().startswith(("http://", "https://")):
        req = urllib.request.Request(
            source,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36"}
        )
        try:
            raw = urllib.request.urlopen(req, timeout=8).read()
        except Exception as e:
            # Fall back to unverified SSL if cert check fails (common on macOS without
            # the 'Install Certificates' post-install step)
            if "CERTIFICATE_VERIFY_FAILED" not in str(e):
                raise
            raw = urllib.request.urlopen(req, timeout=8, context=ssl._create_unverified_context()).read()
        img = Image.open(io.BytesIO(raw))
        img.load()  # fully decode before the BytesIO buffer is garbage collected
        return img
    return Image.open(source)

def loadCardPhoto(source):
    """Return an 88x88 thumbnail PhotoImage, using the cache to avoid reloading."""
    key = str(source)
    if key in thumbCache:
        return thumbCache[key]  # cache hit: skip network/disk IO
    thumb = loadBusinessImage(source).resize((88, 88), Image.LANCZOS)
    photo = ImageTk.PhotoImage(thumb)
    thumbCache[key] = photo  # store reference; GC would otherwise discard it
    return photo

def logImageFailure(source, err):
    """Log an image load failure once per source URL to avoid console spam."""
    key = str(source)
    if key in imageFailLog:
        return  # already logged; don't repeat for every render of the same card
    imageFailLog.add(key)
    print(f"[ImageLoadFail] {key} -> {type(err).__name__}: {err}")

def showBusinesses(df=None):
    """Render the current page of business cards into the scrollable grid.

    If df is provided it replaces the active dataset and resets to page 0.
    If df is None, the existing browseData (last search result) is used.
    """
    global browseData, browsePage
    for w in businessFrame.winfo_children():
        w.destroy()
    if df is not None:
        browseData = df.reset_index(drop=True)
        browsePage = 0  # new search always starts at page 1
    elif browseData is None:
        browseData = businessDatabase.reset_index(drop=True)

    total_results = len(browseData)
    if total_results == 0:
        query = searchVar.get().strip() if "searchVar" in globals() else ""
        if query:
            msg = f'No results for "{query}". Try a different search or clear the filters.'
        else:
            msg = "No businesses found. Check back later!"
        Label(businessFrame, text=msg, font=FONT_H2, fg=TEXT_LT, bg=BG, pady=60, wraplength=400).pack()
        updateBrowsePager(0)
        return

    max_page = max(0, (total_results - 1) // browsePageSize)
    if browsePage > max_page:
        browsePage = max_page
    start_idx = browsePage * browsePageSize
    end_idx = min(start_idx + browsePageSize, total_results)
    page_df = browseData.iloc[start_idx:end_idx]

    businessViewer.update_idletasks()
    available_width = max(businessViewer.winfo_width(), 1)
    min_card_width = 460  # cards narrower than this look squished
    columns = max(1, available_width // min_card_width)
    for c in range(columns):
        # "uniform" forces equal column widths regardless of card content widths
        businessFrame.grid_columnconfigure(c, weight=1, uniform="browse_cards")
    for i, (_, row) in enumerate(page_df.iterrows()):
        grid_row = i // columns
        grid_col = i % columns

        shadowF = Frame(businessFrame, bg=SHADOW)
        shadowF.grid(row=grid_row, column=grid_col, padx=10, pady=8, sticky="nsew")
        card = Frame(shadowF, bg=CARD_BG)
        card.pack(padx=1, pady=1, fill="x")

        imgF = Frame(card, bg="#f1f5f9", width=108, height=108)
        imgF.pack(side="left", padx=14, pady=14)
        imgF.pack_propagate(False)
        try:
            photo = loadCardPhoto(row["Image"])
            lbl = Label(imgF, image=photo, bg=CARD_BG)
            lbl.image = photo
            lbl.pack(expand=True)
        except Exception as e:
            logImageFailure(row["Image"], e)
            Label(imgF, text="🏢", font=("Segoe UI", 30), bg="#f1f5f9", fg=TEXT_LT).pack(expand=True, fill="both")

        infoF = Frame(card, bg=CARD_BG)
        infoF.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=14)

        # Name row with verified badge
        nameRow = Frame(infoF, bg=CARD_BG)
        nameRow.pack(fill="x")
        Label(nameRow, text=row["Name"], font=("Segoe UI", 14, "bold"), fg=TEXT_DK, bg=CARD_BG, anchor="w").pack(side="left")
        if isVerified(row):
            Label(nameRow, text=" ✅", font=("Segoe UI", 11), fg=SUCCESS, bg=CARD_BG).pack(side="left")

        # Category pill
        cat_color = getCategoryColor(row["Category"])
        pillRow = Frame(infoF, bg=CARD_BG)
        pillRow.pack(fill="x", pady=(5, 0))
        Label(pillRow, text=f"  {row['Category']}  ", font=("Segoe UI", 9, "bold"),
              fg=WHITE, bg=cat_color, padx=4, pady=3).pack(side="left")

        # New badge inline
        try:
            added = datetime.date.fromisoformat(str(row.get("DateAdded", "") if hasattr(row, "get") else row["DateAdded"]))
            # 7 days is the window considered "new" for the badge
            if (datetime.date.today() - added).days <= 7:
                Label(pillRow, text="  🆕 New  ", font=("Segoe UI", 9, "bold"),
                      fg=WHITE, bg="#2563eb", padx=4, pady=3).pack(side="left", padx=(6, 0))
        except:
            pass  # missing or malformed DateAdded silently skips the badge

        # Stars
        nr = int(row["Number of Reviews"])
        if nr > 0:
            makeStarRow(infoF, CARD_BG, float(row["Rating"]), nr)
        else:
            Label(infoF, text="Be the first to review!", font=("Segoe UI", 10, "italic"),
                  fg=TEXT_LT, bg=CARD_BG, anchor="w").pack(fill="x", pady=(4, 0))

        # Location
        Label(infoF, text="📍 " + str(row["Location"]), font=("Segoe UI", 10),
              fg=TEXT_MD, bg=CARD_BG, anchor="w").pack(fill="x", pady=(4, 0))

        # Buttons
        btnF = Frame(card, bg=CARD_BG)
        btnF.pack(side="right", padx=20, pady=14)
        makeButton(btnF, "View Details",   lambda r=row: showDetails(r),     style="primary").pack(pady=(0, 8), fill="x")
        makeButton(btnF, "Write a Review", lambda r=row: addReviewScreen(r), style="ghost").pack(pady=(0, 8), fill="x")
        saved_flag = isSaved(row["Name"])
        saveBtn = Button(btnF,
                         text="🔖 Saved" if saved_flag else "🔖 Save",
                         font=FONT_BTN,
                         bg="#dbeafe" if saved_flag else "#eff6ff",
                         fg=PRIMARY,
                         activebackground="#dbeafe", activeforeground=PRIMARY,
                         relief="flat", cursor="hand2", bd=0, padx=16, pady=8)
        saveBtn.config(command=lambda b=row["Name"], s=saveBtn: toggleSave(b, s))
        saveBtn.pack(fill="x")

        # Hover effect: card turns light blue and shadow turns primary blue
        def _enterCard(e, c=card, s=shadowF): c.config(bg=CARD_HOVER); s.config(bg=PRIMARY)
        def _leaveCard(e, c=card, s=shadowF): c.config(bg=CARD_BG);    s.config(bg=SHADOW)
        card.bind("<Enter>", _enterCard)
        card.bind("<Leave>", _leaveCard)
    updateBrowsePager(total_results)
    businessFrame.update_idletasks()
    businessViewer.configure(scrollregion=businessViewer.bbox("all"))
    flushLayout()

# DETAIL WINDOW
def showDetails(business):
    """Open a modal popup with the full business profile, image, and reviews."""
    win = Toplevel(startScreen)
    win.title(business["Name"])
    win.configure(bg=BG)
    win.geometry("580x700")
    win.resizable(True, True)
    win.grab_set()

    hdr = Frame(win, bg=HEADER_BG)
    hdr.pack(fill="x")
    Label(hdr, text=business["Name"], font=("Segoe UI", 17, "bold"), fg=WHITE, bg=HEADER_BG, pady=10, padx=20).pack(anchor="w")
    hdrSub = Frame(hdr, bg=HEADER_BG)
    hdrSub.pack(fill="x", padx=20, pady=(0, 10))
    cat_color = getCategoryColor(business["Category"])
    Label(hdrSub, text=f"  {business['Category']}  ", font=("Segoe UI", 9, "bold"),
          fg=WHITE, bg=cat_color, padx=4, pady=2).pack(side="left")
    if isVerified(business):
        Label(hdrSub, text="  ✅ Verified", font=("Segoe UI", 9, "bold"),
              fg="#86efac", bg=HEADER_BG, padx=8).pack(side="left")

    # Scrollable body
    bodyOuter = Frame(win, bg=BG)
    bodyOuter.pack(fill="both", expand=True)
    bodyCanvas = Canvas(bodyOuter, bg=BG, highlightthickness=0)
    bodySb = Scrollbar(bodyOuter, orient="vertical", command=bodyCanvas.yview)
    bodyCanvas.configure(yscrollcommand=bodySb.set)
    bodyCanvas.pack(side="left", fill="both", expand=True)
    bodySb.pack(side="right", fill="y")
    body = Frame(bodyCanvas, bg=BG, padx=28, pady=18)
    bodyCanvas.create_window((0, 0), window=body, anchor="nw")
    body.bind("<Configure>", lambda e: bodyCanvas.configure(scrollregion=bodyCanvas.bbox("all")))

    try:
        img = loadBusinessImage(business["Image"])
        img.thumbnail((500, 300), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        lbl = Label(body, image=photo, bg=BG)
        lbl.image = photo
        lbl.pack(pady=(0, 14))
    except Exception as e:
        logImageFailure(business["Image"], e)
        Label(body, text="[No Image]", font=FONT_BODY, fg=TEXT_MD, bg=BG).pack(pady=(0, 14))

    for label, value in [("📍 Location", business["Location"]),
                         ("📝 Description", business["Description"])]:
        rowF = Frame(body, bg=BG)
        rowF.pack(fill="x", pady=4)
        Label(rowF, text=f"{label}:", font=("Segoe UI", 11, "bold"), fg=TEXT_DK, bg=BG, width=15, anchor="w").pack(side="left")
        Label(rowF, text=value, font=FONT_BODY, fg=TEXT_MD, bg=BG, anchor="w", wraplength=380).pack(side="left")

    if business["Number of Reviews"] > 0:
        nr = int(business["Number of Reviews"])
        makeStarRow(body, BG, float(business["Rating"]), nr)

    biz_reviews = reviewsDatabase[reviewsDatabase["Business Name"] == business["Name"]]
    if not biz_reviews.empty:
        Label(body, text="Customer Reviews", font=FONT_H2, fg=TEXT_DK, bg=BG).pack(anchor="w", pady=(12, 6))
        revOuter = Frame(body, bg=BG)
        revOuter.pack(fill="x")
        revCanvas = Canvas(revOuter, bg=BG, height=200, highlightthickness=0)
        revScroll = Scrollbar(revOuter, orient="vertical", command=revCanvas.yview)
        revCanvas.configure(yscrollcommand=revScroll.set)
        revCanvas.pack(side="left", fill="both", expand=True)
        revScroll.pack(side="right", fill="y")
        revFrame = Frame(revCanvas, bg=BG)
        revCanvas.create_window((0, 0), window=revFrame, anchor="nw")
        for rev_idx, rev_row in biz_reviews.iterrows():
            rc = Frame(revFrame, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            rc.pack(fill="x", pady=4, padx=2)

            # Avatar + name row
            topRow = Frame(rc, bg=CARD_BG)
            topRow.pack(fill="x", padx=10, pady=(8, 2))
            uname = str(rev_row["Username"]) if str(rev_row["Username"]) not in ("", "nan") else "Anonymous"
            avatarLbl = Label(topRow, text=uname[0].upper(), font=("Segoe UI", 10, "bold"),
                              fg=WHITE, bg=getAvatarColor(uname), width=2, padx=6, pady=4)
            avatarLbl.pack(side="left")
            Label(topRow, text=f"  {uname}", font=("Segoe UI", 10, "bold"), fg=TEXT_DK, bg=CARD_BG).pack(side="left")

            # Stars
            stars_n = int(rev_row["Rating"]) if pd.notna(rev_row["Rating"]) else 0
            Label(rc, text="★"*stars_n + "☆"*(5-stars_n), font=("Segoe UI", 11),
                  fg=STAR_GOLD, bg=CARD_BG, anchor="w", padx=10).pack(fill="x")

            # Review text
            Label(rc, text=str(rev_row["Review"]), font=FONT_SMALL, fg=TEXT_DK, bg=CARD_BG,
                  anchor="w", wraplength=480, justify="left", padx=10).pack(fill="x", pady=(2, 6))

            # Owner reply
            reply_val = rev_row["Reply"] if "Reply" in rev_row.index else ""
            reply = "" if pd.isna(reply_val) else str(reply_val).strip()
            if reply and reply != "nan":
                replyF = Frame(rc, bg="#eff6ff", padx=10, pady=6)
                replyF.pack(fill="x", padx=8, pady=(0, 6))
                Label(replyF, text="💬 Owner Reply:", font=("Segoe UI", 9, "bold"),
                      fg=PRIMARY, bg="#eff6ff", anchor="w").pack(fill="x")
                Label(replyF, text=reply, font=FONT_SMALL, fg=TEXT_DK, bg="#eff6ff",
                      anchor="w", wraplength=440, justify="left").pack(fill="x")

        revFrame.update_idletasks()
        revCanvas.configure(scrollregion=revCanvas.bbox("all"))

    makeButton(body, "Close", win.destroy, style="ghost").pack(pady=(16, 0))

# HOME SCREEN
def setHomeScreen():
    """Build and display the main browse home screen for the logged-in account type."""
    clearScreen()
    global accountInUse
    # Each account type sees a different toolbar (or none for customers)
    acct_type = accountDatabase.loc[accountInUse, "Type"]
    if acct_type == "Owner":
        showToolbar()
        headerLogoutBtn.pack_forget()  # owner uses toolbar logout instead
    else:
        hideToolbar()
        # Customer logout button lives in the header rather than a toolbar
        headerLogoutBtn.pack(side="right", padx=16, fill="y")

    # Search banner
    searchFrame.pack(fill="x")
    searchLabel.pack(side="left", padx=(16, 6), pady=10)
    searchEntry.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=10)
    chooseCategory.pack(side="left", padx=(0, 6), pady=10)
    ratingOrderInput.pack(side="left", padx=(0, 6), pady=10)
    goButton.pack(side="left", padx=(0, 16), pady=10)
    # Save and Profile nav buttons are customer-only
    if acct_type == "Owner":
        savedNavBtn.pack_forget()
        profileNavBtn.pack_forget()
    else:
        savedNavBtn.pack(side="left", padx=(0, 6), pady=10)
        profileNavBtn.pack(side="left", padx=(0, 6), pady=10)
    prevPageButton.pack(side="left", padx=(0, 6), pady=10)
    pageInfoLabel.pack(side="left", padx=(0, 6), pady=10)
    nextPageButton.pack(side="left", padx=(0, 16), pady=10)

    # Scrollbar must be packed before canvas or it won't appear
    viewerScrollbar.pack(side="right", fill="y")
    businessViewer.pack(side="left", fill="both", expand=True)
    showBusinesses(businessDatabase)
    flushLayout()

def sortAndSearch():
    """Filter and sort the business list based on the current search bar state."""
    query = searchVar.get().lower()
    category = chosenCategory.get()
    rating_sort = ratingOrder.get()
    filtered = businessDatabase.copy()
    # Text search checks both Name and Description so partial matches work
    if query:
        filtered = filtered[filtered.apply(
            lambda row: query in row["Name"].lower() or query in row["Description"].lower(), axis=1)]
    # "Sort by Category" is the default/unset sentinel value
    if category != "Sort by Category":
        filtered = filtered[filtered["Category"] == category]
    if rating_sort == "Highest to Lowest Rating":
        filtered = filtered.sort_values(by="Rating", ascending=False)
    elif rating_sort == "Lowest to Highest Rating":
        filtered = filtered.sort_values(by="Rating", ascending=True)
    elif rating_sort == "Most Reviews":
        filtered = filtered.sort_values(by="Number of Reviews", ascending=False)
    showBusinesses(filtered)

# REVIEW SCREEN
def addReviewScreen(business):
    """Open the review submission dialog for the given business."""
    global starButtons, rating
    # Block duplicate reviews before opening the dialog
    username = accountDatabase.loc[accountInUse, "Username"] if accountInUse >= 0 else ""
    already = reviewsDatabase[(reviewsDatabase["Business Name"] == business["Name"]) & (reviewsDatabase["Username"] == username)]
    if not already.empty:
        messagebox.showinfo("Already Reviewed", f"You've already reviewed {business['Name']}.")
        return
    rating.set(0)
    starButtons = []
    win = Toplevel(startScreen)
    win.title("Review — " + business["Name"])
    win.configure(bg=BG)
    win.geometry("520x480")
    win.resizable(False, False)
    win.grab_set()

    hdr = Frame(win, bg=HEADER_BG)
    hdr.pack(fill="x")
    Label(hdr, text="⭐  Write a Review", font=FONT_H1,
          fg=WHITE, bg=HEADER_BG, pady=14, padx=20).pack(anchor="w")
    Label(hdr, text=business["Name"], font=("Segoe UI", 10), fg="#93c5fd", bg=HEADER_BG, padx=20).pack(anchor="w", pady=(0, 8))

    body = Frame(win, bg=BG, padx=28, pady=20)
    body.pack(fill="both", expand=True)

    Label(body, text="How would you rate your experience?", font=FONT_H2, fg=TEXT_DK, bg=BG).pack(pady=(0, 8))
    starFrame = Frame(body, bg=BG)
    starFrame.pack(pady=(0, 14))
    for i in range(5):
        star = Button(starFrame, text="☆", font=("Segoe UI", 32),
                      fg="black", bg=BG, activebackground=BG, activeforeground="red",
                      relief="flat", cursor="hand2", bd=0, command=lambda i=i: setRating(i + 1))
        star.bind("<Enter>", lambda e, s=star: s.config(fg="red"))
        star.bind("<Leave>", lambda e, s=star: s.config(fg="black"))
        star.pack(side="left", padx=4)
        starButtons.append(star)

    Label(body, text="Tell others about your experience:",
          font=FONT_BODY, fg=TEXT_DK, bg=BG).pack(anchor="w", pady=(0, 6))
    reviewDescription = Text(body, height=6, width=46, wrap="word",
                             font=FONT_BODY, fg=TEXT_DK, bg=INPUT_BG,
                             insertbackground=TEXT_DK, relief="flat",
                             highlightthickness=1, highlightbackground=INPUT_BD,
                             highlightcolor=PRIMARY, bd=0, padx=8, pady=6)
    reviewDescription.pack(fill="x")
    addTextPlaceholder(reviewDescription, "Describe your experience here…")

    counterLbl = Label(body, text="0 / 500", font=FONT_SMALL, fg=TEXT_LT, bg=BG, anchor="e")
    counterLbl.pack(fill="x", pady=(2, 0))

    def onReviewType(event=None):
        text = reviewDescription.get("1.0", "end-1c")
        count = len(text)
        if count > 500:
            # Hard-cap at 500 characters by truncating excess on each keystroke
            reviewDescription.delete("1.0", END)
            reviewDescription.insert("1.0", text[:500])
            count = 500
        # Counter turns red when approaching the limit to warn the user
        counterLbl.config(text=f"{count} / 500",
                          fg=ERROR_RED if count >= 480 else TEXT_LT)

    reviewDescription.bind("<KeyRelease>", onReviewType)

    Label(body, text="Tip: Be honest and specific — your review helps others!",
          font=("Segoe UI", 9, "italic"), fg=TEXT_LT, bg=BG, anchor="w").pack(fill="x", pady=(4, 0))

    errorLbl = Label(body, text="", font=FONT_SMALL, fg=ERROR_RED, bg=BG)
    errorLbl.pack(pady=(4, 0))

    def submitReview():
        if rating.get() == 0:
            errorLbl.config(text="Please select a star rating.")
            return
        rev_text = reviewDescription.get("1.0", "end-1c")
        updateReview(business, rev_text)
        win.destroy()

    makeButton(body, "Submit Review", submitReview, style="primary").pack(pady=(8, 0))

def setRating(value):
    """Store the selected star rating and update the visual star buttons."""
    global rating
    rating.set(value)
    updateStars()

def updateStars():
    """Re-render the star buttons to reflect the current rating value."""
    global starButtons, rating
    for i in range(5):
        # Filled star for all positions up to the rating, empty beyond
        starButtons[i].config(text="★" if i < rating.get() else "☆")

def updateReview(row, review):
    """Append a new review to the reviews table and update the business stats."""
    global rating, accountInUse, reviewsDatabase
    review = review.strip()
    # Reject empty review or the placeholder text left in the Text widget
    if review in ("", "Describe your experience here…"):
        return
    if rating.get() == 0:
        return
    username = accountDatabase.loc[accountInUse, "Username"] if accountInUse >= 0 else ""
    already = reviewsDatabase[(reviewsDatabase["Business Name"] == row["Name"]) & (reviewsDatabase["Username"] == username)]
    if not already.empty:
        return  # duplicate guard: the dialog already warned them, just silently exit
    # Coerce to list in case CSV loaded the Reviews column as a string
    if not isinstance(accountDatabase.loc[accountInUse, "Reviews"], list):
        accountDatabase.loc[accountInUse, "Reviews"] = []
    username = accountDatabase.loc[accountInUse, "Username"] if accountInUse >= 0 else ""
    new_row = {"Business Name": row["Name"], "Username": username, "Rating": int(rating.get()), "Review": review, "Reply": ""}
    # Only set Reported if the column already exists (older CSVs may not have it)
    if "Reported" in reviewsDatabase.columns:
        new_row["Reported"] = False
    # Build row list in column order so it appends correctly regardless of column sequence
    reviewsDatabase.loc[len(reviewsDatabase)] = [new_row.get(c, "") for c in reviewsDatabase.columns]
    accountDatabase.loc[accountInUse, "Reviews"].append({"rating": rating.get(), "review": review})
    accountDatabase.loc[accountInUse, "Number of Reviews"] += 1
    refreshBusinessReviewsFromTable()
    saveData()
    setHomeScreen()

def showHelp():
    win = Toplevel(startScreen)
    win.title("Help — CityPulse")
    win.configure(bg=CARD_BG)
    win.geometry("500x600")
    win.resizable(False, True)
    win.grab_set()

    hdr = Frame(win, bg=HEADER_BG)
    hdr.pack(fill="x")
    Label(hdr, text="📖  Help & Guide", font=FONT_H1, fg=WHITE, bg=HEADER_BG, pady=14, padx=20).pack(anchor="w")
    Label(hdr, text="Everything you need to know about CityPulse",
          font=FONT_SMALL, fg="#93c5fd", bg=HEADER_BG, padx=2 ).pack(anchor="w",pady=(0, 10))

    # Scrollable body
    outer = Frame(win, bg=CARD_BG)
    outer.pack(fill="both", expand=True)
    canvas = Canvas(outer, bg=CARD_BG, highlightthickness=0)
    sb = Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    body = Frame(canvas, bg=CARD_BG, padx=24, pady=16)
    canvas.create_window((0, 0), window=body, anchor="nw")
    body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Enter>", lambda e, c=canvas: setActiveScrollCanvas(c))
    canvas.bind("<Leave>", lambda e: setActiveScrollCanvas(None))

    sections = [
        ("🔍  Searching & Browsing",
         "Type a business name or keyword into the search bar and press Search or hit Enter. "
         "Use the Category dropdown to filter by type (Food, Retail, Health, etc.). "
         "Sort results by Highest or Lowest rating using the rating dropdown. "
         "Use the ← Prev and Next → buttons to page through results when there are many listings."),

        ("📋  Viewing Business Details",
         "Click View Details on any business card to open a full profile showing the business image, "
         "location, category, description, star rating, and all customer reviews. "
         "Owner replies to reviews are shown in blue below each review."),

        ("⭐  Leaving a Review",
         "Click Add Review on any business card. Select 1–5 stars by clicking the star buttons, "
         "then write about your experience in the text box and click Submit Review. "
         "You must be logged in as a Customer to leave reviews. "
         "Your review will appear immediately on the business profile."),

        ("🔖  Saving Businesses",
         "Click the 🔖 Save button on any business card to bookmark it for later. "
         "Saved businesses are accessible from the 🔖 My Saved button in the search bar. "
         "To remove a bookmark, click 🔖 Remove on the saved list or click the button again on the card."),

        ("🔑  Creating an Account",
         "Click Create New Account on the welcome screen. Enter a username, email, and password, "
         "then choose whether you are a Customer or a Business Owner. "
         "Customers can browse, review, and save businesses. "
         "Business Owners can list and manage their own businesses."),

        ("🏢  Adding Your Business (Owners)",
         "After logging in as an Owner, click ＋ Add Business in the toolbar. "
         "Fill in your business name, category, location, and description. "
         "Upload a business image and a valid business license (PDF or image file). "
         "A green ✓ appears next to each upload box when the file is ready. "
         "Click Create Business to publish your listing."),

        ("✏️  Managing Your Businesses (Owners)",
         "Go to 🏢 My Businesses in the toolbar to see all your listings. "
         "Click Edit to update any business details or swap the image. "
         "Click View Reviews to read all customer reviews for that business and reply to them. "
         "Click Delete to permanently remove a listing and all its reviews."),

        ("💬  Replying to Reviews (Owners)",
         "Open View Reviews from My Businesses. Each review shows a 💬 Reply button. "
         "Click it to write a public reply — customers will see your response under their review "
         "in the View Details window. Click Edit Reply at any time to update your response."),

        ("📄  Business License Requirement",
         "A business license upload is required when creating a new listing. "
         "This helps verify that the business is legitimate. "
         "Accepted formats: PDF, PNG, JPG, JPEG. The file is stored locally and not shared publicly."),

        ("🚪  Logging Out",
         "Customers: click Log Out in the top-right corner of the header. "
         "Business Owners: click Log Out on the right end of the owner toolbar. "
         "You will be returned to the welcome screen and your session will end."),
    ]

    for title, desc in sections:
        sF = Frame(body, bg="#f8fafc", highlightthickness=1, highlightbackground=BORDER)
        sF.pack(fill="x", pady=5)
        Label(sF, text=title, font=FONT_H2, fg=TEXT_DK, bg="#f8fafc",
              anchor="w", padx=12).pack(fill="x", pady=(8, 2))
        Label(sF, text=desc, font=FONT_BODY, fg=TEXT_MD, bg="#f8fafc",
              anchor="w", wraplength=420, justify="left", padx=12, pady=8).pack(fill="x")

    foot = Frame(win, bg=CARD_BG, padx=24, pady=10)
    foot.pack(fill="x")
    makeButton(foot, "Close", win.destroy, style="ghost").pack(anchor="e")

def saveData():
    """Persist all three DataFrames to their CSV files on disk."""
    accountDatabase.to_csv(ACCOUNTS_CSV, index=False)
    businessDatabase.to_csv(BUSINESSES_CSV, index=False)
    reviewsDatabase.to_csv(REVIEWS_CSV, index=False)

# MAIN WINDOW
startScreen = Tk()
startScreen.title("CityPulse")
startScreen.state("zoomed")  # start maximized on all platforms
startScreen.configure(bg=HEADER_BG)

applyStyles()

accountInUse      = -1   # -1 means no user is logged in
filePath          = ""   # holds the chosen business image path during form entry
licensePath       = ""   # holds the chosen license file path during form entry
licenseUploadBtn  = None
imageCheckLabel   = None
licenseCheckLabel = None
currentBusinessIndex = -1  # -1 means no business is being edited
rating           = IntVar(value=0)
starButtons      = []

# Data
def _parseList(x):
    """Coerce a CSV cell value to a Python list, handling string-encoded lists."""
    if isinstance(x, list): return x
    if pd.isna(x): return []
    try:
        # ast.literal_eval safely parses "['a', 'b']" strings back to lists
        parsed = ast.literal_eval(str(x).strip())
        return parsed if isinstance(parsed, list) else []
    except: return []

if os.path.exists(ACCOUNTS_CSV):
    accountDatabase = pd.read_csv(ACCOUNTS_CSV)
    # These columns are stored as "[…]" strings in CSV; coerce back to real lists
    accountDatabase["Businesses"] = accountDatabase["Businesses"].apply(_parseList)
    accountDatabase["Reviews"]    = accountDatabase["Reviews"].apply(_parseList)
    # "Saved" column was added in a later version; migrate old CSVs gracefully
    if "Saved" not in accountDatabase.columns:
        accountDatabase["Saved"] = [[] for _ in range(len(accountDatabase))]
    else:
        accountDatabase["Saved"] = accountDatabase["Saved"].apply(_parseList)
else:
    accountDatabase = pd.DataFrame(columns=["Username","Password","Email","Number of Reviews","Certificates","Reviews","Type","Businesses"])

if os.path.exists(BUSINESSES_CSV):
    businessDatabase = pd.read_csv(BUSINESSES_CSV)
    businessDatabase["Reviews"] = businessDatabase["Reviews"].apply(_parseList)
    # "License" and "DateAdded" were added in later versions; migrate older CSVs
    if "License" not in businessDatabase.columns:
        businessDatabase["License"] = ""
    if "DateAdded" not in businessDatabase.columns:
        businessDatabase["DateAdded"] = ""
else:
    businessDatabase = pd.DataFrame(columns=["Name","Location","Image","Description","Category","Rating","Number of Reviews","Total Rating Count","Reviews","License","DateAdded"])

if os.path.exists(REVIEWS_CSV):
    reviewsDatabase = pd.read_csv(REVIEWS_CSV)
else:
    reviewsDatabase = pd.DataFrame(columns=["Business Name", "Username", "Rating", "Review"])
    # One-time migration: unpack reviews embedded in businesses.csv into reviews.csv
    # Legacy format stored reviews as "3★ - great food" strings inside each business row
    for _, biz in businessDatabase.iterrows():
        biz_name = biz.get("Name", "")
        raw_reviews = biz.get("Reviews", [])
        if not isinstance(raw_reviews, list):
            continue
        for item in raw_reviews:
            text = str(item)
            match = re.match(r"^\s*(\d+)\s*★\s*-\s*(.*)$", text)
            if match:
                r = int(match.group(1))
                msg = match.group(2).strip()
            else:
                r = 0
                msg = text.strip()
            reviewsDatabase.loc[len(reviewsDatabase)] = [biz_name, "", r, msg]

# Ensure all required columns exist (handles old CSV schemas)
for col in ["Business Name", "Username", "Rating", "Review"]:
    if col not in reviewsDatabase.columns:
        reviewsDatabase[col] = "" if col in ("Business Name", "Username", "Review") else 0

if "Reply" not in reviewsDatabase.columns:
    reviewsDatabase["Reply"] = ""
else:
    reviewsDatabase["Reply"] = reviewsDatabase["Reply"].fillna("")  # NaN -> empty string

if "Reported" not in reviewsDatabase.columns:
    reviewsDatabase["Reported"] = False
else:
    reviewsDatabase["Reported"] = reviewsDatabase["Reported"].fillna(False)  # NaN -> False

def refreshBusinessReviewsFromTable():
    """Recompute each business's rating stats from the reviews table.

    This keeps businessDatabase.Rating and Number of Reviews in sync
    with reviewsDatabase after any add, delete, or migration operation.
    """
    if "Reviews" not in businessDatabase.columns:
        businessDatabase["Reviews"] = [[] for _ in range(len(businessDatabase))]
    for idx in businessDatabase.index:
        biz_name = businessDatabase.loc[idx, "Name"]
        subset = reviewsDatabase[reviewsDatabase["Business Name"] == biz_name]
        ratings = pd.to_numeric(subset["Rating"], errors="coerce").fillna(0)
        total = int(ratings.sum())
        count = int(len(subset))
        businessDatabase.loc[idx, "Total Rating Count"] = total
        businessDatabase.loc[idx, "Number of Reviews"] = count
        # Avoid division by zero for businesses with no reviews
        businessDatabase.loc[idx, "Rating"] = (total / count) if count > 0 else 0.0
        # Denormalized text copy kept for legacy CSV compatibility
        businessDatabase.at[idx, "Reviews"] = [
            f"{int(r)}★ - {str(t).strip()}"
            for r, t in zip(ratings.tolist(), subset["Review"].fillna("").tolist())
        ]

# Deduplicate reviews: keep only the first review per (Business Name, Username) pair.
# Named users can only have one review per business; anonymous migrations also deduplicate.
reviewsDatabase = reviewsDatabase.drop_duplicates(
    subset=["Business Name", "Username"], keep="first"
).reset_index(drop=True)

refreshBusinessReviewsFromTable()

# Permanent header
headerFrame = Frame(startScreen, bg=HEADER_BG, height=64)
headerFrame.pack(fill="x", side="top")
headerFrame.pack_propagate(False)  # lock header to exactly 64px tall
Label(headerFrame, text="🏙  CityPulse", font=FONT_TITLE,
      fg=WHITE, bg=HEADER_BG, padx=24).pack(side="left", fill="y")

headerLogoutBtn = Button(headerFrame, text="Log Out", font=FONT_TB,
                         bg=HEADER_BG, fg="black", activebackground=ERROR_RED,
                         activeforeground=WHITE, relief="flat", cursor="hand2",
                         bd=0, padx=18, command=logOut)
headerLogoutBtn.bind("<Enter>", lambda e: headerLogoutBtn.config(bg=ERROR_RED))
headerLogoutBtn.bind("<Leave>", lambda e: headerLogoutBtn.config(bg=HEADER_BG))
# starts hidden; pack_forget keeps it off screen until a customer logs in

helpBtn = Button(headerFrame, text=" ? ", font=("Segoe UI", 13, "bold"),
                 bg="#3b82f6", fg="black", activebackground="#2563eb", activeforeground=WHITE,
                 relief="flat", cursor="hand2", bd=0, padx=12, pady=6,
                 command=showHelp)
helpBtn.bind("<Enter>", lambda e: helpBtn.config(bg="#2563eb"))
helpBtn.bind("<Leave>", lambda e: helpBtn.config(bg="#3b82f6"))
helpBtn.pack(side="right", padx=(0, 12), pady=12)

# Owner toolbar (shown after login, hidden on auth)
toolbar = Frame(startScreen, bg=TOOLBAR_BG)
# toolbar is intentionally not packed here; showToolbar/hideToolbar manage its visibility

# Main content area
mainContent = Frame(startScreen, bg=BG)
mainContent.pack(fill="both", expand=True)

# Auth widgets
authWrapper = Frame(mainContent, bg=BG)
authCard = Frame(authWrapper, bg=CARD_BG, padx=52, pady=44,
                 highlightthickness=1, highlightbackground=BORDER)
authCard.pack(padx=20, pady=50)

Label(authCard, text="🏙", font=("Segoe UI", 42), fg=PRIMARY, bg=CARD_BG).pack(pady=(0, 8))
Label(authCard, text="Welcome to CityPulse", font=("Segoe UI", 20, "bold"), fg=TEXT_DK, bg=CARD_BG).pack(pady=(0, 4))
Label(authCard, text="Find, review, and save the best local businesses",
      font=("Segoe UI", 11), fg=TEXT_MD, bg=CARD_BG).pack(pady=(0, 28))

usernameInput = makeEntry(authCard, width=32)
addPlaceholder(usernameInput, "Enter Username")
passwordInput = makeEntry(authCard, width=32)
addPlaceholder(passwordInput, "Enter Password")
emailInput = makeEntry(authCard, width=32)
addPlaceholder(emailInput, "Enter Email")
startText = Label(authCard, text="", font=FONT_BODY, fg=ERROR_RED, bg=CARD_BG)

createNewAccountButton       = makeButton(authCard, "Create New Account",        newAccountScreen, style="ghost",   width=26)
loginButton                  = makeButton(authCard, "Login to Existing Account", loginScreen,      style="primary", width=26)
loginCompletedButton         = makeButton(authCard, "Login",          lambda: login(usernameInput.get(), passwordInput.get()), style="primary", width=26)
createAccountCompletedButton = makeButton(authCard, "Create Account", lambda: accountType(),                                   style="primary", width=26)
customerButton = makeButton(authCard, "I'm a Customer",       lambda: createAccount(usernameInput.get(), passwordInput.get(), emailInput.get(), "Customer"), style="primary", width=26)
ownerButton    = makeButton(authCard, "I'm a Business Owner", lambda: createAccount(usernameInput.get(), passwordInput.get(), emailInput.get(), "Owner"),    style="ghost",   width=26)

# Tab cycles focus between auth fields; Enter submits the active form
usernameInput.bind("<Tab>",    lambda e: (emailInput.focus_set()    if emailInput.winfo_ismapped() else passwordInput.focus_set(), "break")[1])
emailInput.bind   ("<Tab>",    lambda e: (passwordInput.focus_set(), "break")[1])
passwordInput.bind("<Tab>",    lambda e: (usernameInput.focus_set(), "break")[1])
usernameInput.bind("<Return>", lambda e: (passwordInput.focus_set() if not loginCompletedButton.winfo_ismapped() else login(usernameInput.get(), passwordInput.get())))
emailInput.bind   ("<Return>", lambda e: passwordInput.focus_set())
passwordInput.bind("<Return>", lambda e: login(usernameInput.get(), passwordInput.get()) if loginCompletedButton.winfo_ismapped() else accountType())

# Show initial auth screen
authWrapper.pack(fill="both", expand=True)
createNewAccountButton.pack(pady=(0, 8))
loginButton.pack()

# Business form widgets (children of mainContent)
businessNameInput = makeEntry(mainContent, width=36)
addPlaceholder(businessNameInput, "Business Name")
businessLocationInput = makeEntry(mainContent, width=36)
addPlaceholder(businessLocationInput, "Business Location")
selectedCategory = StringVar()
businessCategoryInput = ttk.Combobox(mainContent,
    values=["Food","Service","Retail","Health & Wellness","Education",
            "Automotive","Travel & Hospitality","Entertainment","Home Services"],
    textvariable=selectedCategory, state="readonly", width=34, font=FONT_BODY)
businessCategoryInput.set("Select Category")
businessDescriptionInput = makeEntry(mainContent, width=36)
addPlaceholder(businessDescriptionInput, "Business Description")
businessImageInput   = makeButton(mainContent, "Upload Business Image", uploadFile, style="ghost")
createBusinessButton = makeButton(mainContent, "Create Business",
    lambda: createBusiness(businessNameInput.get(), businessLocationInput.get(), businessDescriptionInput.get()),
    style="primary")
createBusinessText  = Label(mainContent, text="", font=FONT_BODY, fg=ERROR_RED, bg=BG)
createBusinessTitle = Label(mainContent, text="Create Your Business", font=FONT_H1, fg=TEXT_DK, bg=BG)

# Edit business widgets
editBusinessNameInput = makeEntry(mainContent, width=36)
addPlaceholder(editBusinessNameInput, "Business Name")
editBusinessLocationInput = makeEntry(mainContent, width=36)
addPlaceholder(editBusinessLocationInput, "Business Location")
editSelectedCategory = StringVar()
editBusinessCategoryInput = ttk.Combobox(mainContent,
    values=["Food","Service","Retail","Health & Wellness","Education",
            "Automotive","Travel & Hospitality","Entertainment","Home Services"],
    textvariable=editSelectedCategory, state="readonly", width=34, font=FONT_BODY)
editBusinessCategoryInput.set("Select Category")
editBusinessDescriptionInput = makeEntry(mainContent, width=36)
addPlaceholder(editBusinessDescriptionInput, "Business Description")
editBusinessImageInput = makeButton(mainContent, "Upload New Image", uploadFile, style="ghost")
editBusinessButton     = makeButton(mainContent, "Save Changes", finalizeEdits, style="success")
editBusinessTitle      = Label(mainContent, text="Edit Business", font=FONT_H1, fg=TEXT_DK, bg=BG)

# Business canvas + scrollbar
businessViewer  = Canvas(mainContent, bg=BG, highlightthickness=0)
viewerScrollbar = Scrollbar(mainContent, orient="vertical", command=businessViewer.yview)
businessViewer.configure(yscrollcommand=viewerScrollbar.set)
businessFrame = Frame(businessViewer, bg=BG)
# Embed businessFrame inside the canvas so it scrolls as one unit
businessViewer.create_window((0, 0), window=businessFrame, anchor="nw")
# on_frame_configure updates the scrollregion whenever the grid grows
businessFrame.bind("<Configure>", on_frame_configure)
businessViewer.bind("<Enter>", lambda e, c=businessViewer: setActiveScrollCanvas(c))
businessViewer.bind("<Leave>", lambda e: setActiveScrollCanvas(None))

# Search bar (child of mainContent)
searchFrame = Frame(mainContent, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
searchLabel = Label(searchFrame, text="🔍  Find:", font=FONT_BTN, fg=TEXT_DK, bg=CARD_BG)
searchVar   = StringVar()
searchEntry = Entry(searchFrame, textvariable=searchVar, font=FONT_BODY,
                    bg=INPUT_BG, fg=TEXT_DK, relief="flat",
                    highlightthickness=1, highlightbackground=INPUT_BD,
                    highlightcolor=PRIMARY, bd=0, width=26, insertbackground=TEXT_DK)
searchEntry.bind("<Return>", lambda e: sortAndSearch())  # allow pressing Enter to search

chosenCategory = StringVar()
chooseCategory = ttk.Combobox(searchFrame,
    values=["Food","Service","Retail","Health & Wellness","Education",
            "Automotive","Travel & Hospitality","Entertainment","Home Services"],
    textvariable=chosenCategory, state="readonly", width=18, font=FONT_BODY)
chooseCategory.set("Sort by Category")

ratingOrder = StringVar()
ratingOrderInput = ttk.Combobox(searchFrame,
    values=["Highest to Lowest Rating","Lowest to Highest Rating","Most Reviews"],
    textvariable=ratingOrder, state="readonly", width=22, font=FONT_BODY)
ratingOrderInput.set("Sort by Rating")

goButton = makeButton(searchFrame, "Search", sortAndSearch, style="primary")
prevPageButton = makeButton(searchFrame, "← Prev", lambda: changeBrowsePage(-1), style="ghost")
pageInfoLabel = Label(searchFrame, text="Page 1/1 (0 results)", font=FONT_SMALL, fg=TEXT_DK, bg=CARD_BG)
nextPageButton = makeButton(searchFrame, "Next →", lambda: changeBrowsePage(1), style="ghost")
savedNavBtn = makeButton(searchFrame, "🔖 My Saved", showSavedBusinesses, style="ghost")
profileNavBtn = makeButton(searchFrame, "👤 Profile", showProfile, style="ghost")

# Launch
# Bind mousewheel globally so any canvas under the cursor receives scroll events
startScreen.bind_all("<MouseWheel>", onGlobalMousewheel)
startScreen.bind_all("<Button-4>", onGlobalMousewheel)   # Linux scroll up
startScreen.bind_all("<Button-5>", onGlobalMousewheel)   # Linux scroll down
startScreen.mainloop()
