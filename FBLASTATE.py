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
from tkinter import font as tkfont

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_CSV = os.path.join(APP_DIR, "accounts.csv")
BUSINESSES_CSV = os.path.join(APP_DIR, "businesses.csv")
REVIEWS_CSV = os.path.join(APP_DIR, "reviews.csv")

# ============================================================
# DESIGN SYSTEM
# ============================================================
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

# ============================================================
# TTK STYLE
# ============================================================
def applyStyles():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TCombobox",
        fieldbackground=INPUT_BG, background=INPUT_BG,
        foreground=TEXT_DK, bordercolor=INPUT_BD,
        lightcolor=INPUT_BD, darkcolor=INPUT_BD,
        relief="flat", padding=(8, 6), font=FONT_BODY)
    style.map("TCombobox", fieldbackground=[("readonly", INPUT_BG)])

# ============================================================
# WIDGET HELPERS
# ============================================================
def makeButton(parent, text, command, style="primary", width=None):
    if style == "primary":  bg, abg = PRIMARY, PRIMARY_DK
    elif style == "ghost":  bg, abg = "#eff6ff", "#dbeafe"
    elif style == "danger": bg, abg = ERROR_RED, "#b91c1c"
    elif style == "success":bg, abg = SUCCESS, "#15803d"
    elif style == "toolbar":bg, abg = TOOLBAR_BG, PRIMARY
    elif style == "blac": bg, abg = "black", "#000000"
    else:                   bg, abg = PRIMARY, PRIMARY_DK
    fg = "black"
    afg = "red"
    kw = dict(text=text, command=command, font=FONT_BTN,
              bg=bg, fg=fg, activebackground=abg, activeforeground=afg,
              relief="flat", cursor="hand2", bd=0, padx=16, pady=8)
    if width: kw["width"] = width
    btn = Button(parent, **kw)
    btn.bind("<Enter>", lambda e: btn.config(bg=abg, fg="red"))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg, fg=fg))
    return btn

def isDarkColor(hex_color):
    c = hex_color.lstrip("#")
    if len(c) != 6:
        return False
    r = int(c[0:2], 16)
    g = int(c[2:4], 16)
    b = int(c[4:6], 16)
    luminance = (0.299 * r) + (0.587 * g) + (0.114 * b)
    return luminance < 150

def makeEntry(parent, width=30, show=None):
    kw = dict(font=FONT_BODY, bg=INPUT_BG, fg=TEXT_DK,
              insertbackground=TEXT_DK, relief="flat",
              highlightthickness=1, highlightbackground=INPUT_BD,
              highlightcolor=PRIMARY, bd=0, width=width)
    if show: kw["show"] = show
    return Entry(parent, **kw)

def addPlaceholder(entry, placeholderText):
    entry.insert(0, placeholderText)
    entry.config(fg="grey")
    def on_focus_in(event):
        if entry.get() == placeholderText:
            entry.delete(0, END)
            entry.config(fg=TEXT_DK)
    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholderText)
            entry.config(fg="grey")
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def addTextPlaceholder(text_widget, placeholder):
    text_widget.insert("1.0", placeholder)
    text_widget.config(fg="grey")
    def on_focus_in(event):
        if text_widget.get("1.0", "end-1c") == placeholder:
            text_widget.delete("1.0", END)
            text_widget.config(fg=TEXT_DK)
    def on_focus_out(event):
        if text_widget.get("1.0", "end-1c") == "":
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg="grey")
    text_widget.bind("<FocusIn>", on_focus_in)
    text_widget.bind("<FocusOut>", on_focus_out)

# ============================================================
# clearScreen — hides all children of mainContent
# ============================================================
def clearScreen():
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

# ============================================================
# TOOLBAR (shown when logged in as Owner)
# ============================================================
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
    toolbar.pack_forget()
    for w in toolbar.winfo_children():
        w.destroy()

# ============================================================
# AUTH SCREENS
# ============================================================
def showAuthScreen():
    hideToolbar()
    clearScreen()
    authWrapper.pack(fill="both", expand=True)
    flushLayout()

def loginScreen():
    showAuthScreen()
    usernameInput.pack(pady=(0, 8))
    passwordInput.pack(pady=(0, 8))
    emailInput.pack_forget()
    startText.pack_forget()
    loginCompletedButton.pack(pady=(4, 0))
    createAccountCompletedButton.pack_forget()
    startText.pack(pady=(8, 0))

def newAccountScreen():
    showAuthScreen()
    usernameInput.pack(pady=(0, 8))
    emailInput.pack(pady=(0, 8))
    passwordInput.pack(pady=(0, 8))
    startText.pack_forget()
    createAccountCompletedButton.pack(pady=(4, 0))
    loginCompletedButton.pack_forget()
    startText.pack(pady=(8, 0))

def login(username, password):
    index = accountDatabase.index[accountDatabase["Username"] == username].tolist()
    if not index:
        startText.config(text="Account Not Found", fg=ERROR_RED)
    elif accountDatabase.loc[index[0], "Password"] != password:
        startText.config(text="Incorrect Password", fg=ERROR_RED)
    else:
        global accountInUse
        accountInUse = index[0]
        setHomeScreen()

def createAccount(username, password, email, type):
    index = accountDatabase.index[accountDatabase["Username"] == username].tolist()
    if index:
        startText.config(text="Username is Unavailable", fg=ERROR_RED)
    else:
        global accountInUse
        accountInUse = len(accountDatabase)
        accountDatabase.loc[len(accountDatabase)] = [username, password, email, 0, [], [], type, []]
        saveData()
        setHomeScreen()

def accountType():
    if usernameInput.get() in ("Enter Username", ""):
        startText.config(text="Enter a valid username", fg=ERROR_RED)
    elif emailInput.get() in ("Enter Email", ""):
        startText.config(text="Enter a valid email", fg=ERROR_RED)
    elif passwordInput.get() in ("Enter Password", ""):
        startText.config(text="Enter a valid password", fg=ERROR_RED)
    else:
        showAuthScreen()
        startText.config(text="I am a...", fg=TEXT_DK, font=FONT_H1, bg=CARD_BG)
        startText.pack(pady=(20, 12))
        customerButton.pack(pady=(0, 8))
        ownerButton.pack(pady=(0, 8))

def logOut():
    global accountInUse
    accountInUse = -1
    usernameInput.delete(0, END); usernameInput.insert(0, "Enter Username"); usernameInput.config(fg="grey")
    passwordInput.delete(0, END); passwordInput.insert(0, "Enter Password"); passwordInput.config(fg="grey")
    emailInput.delete(0, END);    emailInput.insert(0, "Enter Email");       emailInput.config(fg="grey")
    showAuthScreen()
    createNewAccountButton.pack(pady=(0, 8))
    loginButton.pack()

# ============================================================
# BUSINESS FORM — Add
# ============================================================
def uploadFile():
    global filePath
    filePath = filedialog.askopenfilename()
    if filePath:
        businessImageInput.config(bg=SUCCESS, fg=WHITE if isDarkColor(SUCCESS) else TEXT_DK)
        createBusinessText.config(text="Image selected!", fg=SUCCESS)
    else:
        createBusinessText.config(text="No file selected", fg=ERROR_RED)

def addBusinessScreen():
    global businessNameInput, businessLocationInput, businessDescriptionInput
    global selectedCategory, businessCategoryInput
    global businessImageInput, createBusinessButton, createBusinessText
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

    businessImageInput = makeButton(card, "Upload Business Image", uploadFile, style="ghost")
    businessImageInput.config(bg="#eff6ff", fg=WHITE if isDarkColor("#eff6ff") else TEXT_DK)

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
    businessImageInput.pack(pady=(0, 8), fill="x")
    createBusinessButton.pack(pady=(12, 4), fill="x")
    createBusinessText.pack(pady=(4, 0))
    flushLayout()

def createBusiness(name, location, description):
    global filePath, accountInUse
    index = businessDatabase.index[businessDatabase["Name"] == name].tolist()
    if index:                                         createBusinessText.config(text="Business Already Created", fg=ERROR_RED)
    elif businessNameInput.get() == "Business Name":  createBusinessText.config(text="Enter valid name", fg=ERROR_RED)
    elif businessLocationInput.get() == "Business Location": createBusinessText.config(text="Enter valid location", fg=ERROR_RED)
    elif selectedCategory.get() == "Select Category": createBusinessText.config(text="Select a category", fg=ERROR_RED)
    elif businessDescriptionInput.get() == "Business Description": createBusinessText.config(text="Enter valid description", fg=ERROR_RED)
    elif not filePath:                                createBusinessText.config(text="Upload an image", fg=ERROR_RED)
    else:
        businessDatabase.loc[len(businessDatabase)] = [name, location, filePath, description, selectedCategory.get(), 0.0, 0, 0, []]
        if not isinstance(accountDatabase.at[accountInUse, "Businesses"], list):
            accountDatabase.at[accountInUse, "Businesses"] = []
        accountDatabase.at[accountInUse, "Businesses"].append(name)
        saveData()
        filePath = ""
        setHomeScreen()

# ============================================================
# BUSINESS FORM — Edit
# ============================================================
def updateBusiness(updatedValue, type, index):
    if type == "Name":        businessDatabase.loc[index, "Name"] = updatedValue
    if type == "Location":    businessDatabase.loc[index, "Location"] = updatedValue
    if type == "Description": businessDatabase.loc[index, "Description"] = updatedValue
    if type == "Category":    businessDatabase.loc[index, "Category"] = updatedValue
    if type == "Image":       businessDatabase.loc[index, "Image"] = updatedValue

def editBusiness(item):
    global currentBusinessIndex
    global editBusinessNameInput, editBusinessLocationInput, editBusinessDescriptionInput
    global editSelectedCategory, editBusinessCategoryInput, editBusinessImageInput, editBusinessButton
    clearScreen()
    indexlist = businessDatabase.index[businessDatabase["Name"] == item].tolist()
    if not indexlist: return
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
    global currentBusinessIndex, filePath, reviewsDatabase
    index = currentBusinessIndex
    if index < 0 or index not in businessDatabase.index:
        return
    old_name = str(businessDatabase.loc[index, "Name"])
    if editBusinessNameInput.get() not in ("", "Business Name"):         updateBusiness(editBusinessNameInput.get(), "Name", index)
    if editBusinessLocationInput.get() not in ("", "Business Location"): updateBusiness(editBusinessLocationInput.get(), "Location", index)
    if editBusinessDescriptionInput.get() not in ("", "Business Description"): updateBusiness(editBusinessDescriptionInput.get(), "Description", index)
    if editSelectedCategory.get() != "Select Category":                  updateBusiness(editSelectedCategory.get(), "Category", index)
    if filePath:
        updateBusiness(filePath, "Image", index)
        filePath = ""
    new_name = str(businessDatabase.loc[index, "Name"])
    if new_name != old_name:
        # Keep owner business references in sync when a business is renamed.
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
    global reviewsDatabase
    if not messagebox.askyesno("Delete Business", f"Delete '{item}'? This will remove its reviews too."):
        return
    indexlist = businessDatabase.index[businessDatabase["Name"] == item].tolist()
    if indexlist:
        businessDatabase.drop(index=indexlist[0], inplace=True)
        businessDatabase.reset_index(drop=True, inplace=True)
    # Remove deleted business from all accounts' owned business lists.
    for acc_idx in accountDatabase.index:
        businesses = accountDatabase.loc[acc_idx, "Businesses"]
        if isinstance(businesses, list):
            accountDatabase.at[acc_idx, "Businesses"] = [b for b in businesses if b != item]
    # Drop all persisted reviews for the deleted business.
    if "Business Name" in reviewsDatabase.columns:
        reviewsDatabase = reviewsDatabase[reviewsDatabase["Business Name"] != item].reset_index(drop=True)
    refreshBusinessReviewsFromTable()
    saveData()
    showOwnerBusinesses()

# ============================================================
# OWNER — My Businesses screen
# ============================================================
def viewBusinessReviews(biz_name):
    """Open a popup showing all reviews for a business the owner owns."""
    indexlist = businessDatabase.index[businessDatabase["Name"] == biz_name].tolist()
    if not indexlist:
        return
    idx = indexlist[0]
    row = businessDatabase.loc[idx]
    reviews = row["Reviews"] if isinstance(row["Reviews"], list) else []

    win = Toplevel(startScreen)
    win.title(f"Reviews — {biz_name}")
    win.configure(bg=BG)
    win.geometry("540x500")
    win.grab_set()

    hdr = Frame(win, bg=HEADER_BG)
    hdr.pack(fill="x")
    Label(hdr, text=f"Reviews: {biz_name}", font=FONT_H1,
          fg=WHITE, bg=HEADER_BG, pady=14, padx=20).pack(anchor="w")

    body = Frame(win, bg=CARD_BG, padx=24, pady=16)
    body.pack(fill="both", expand=True)

    if row["Number of Reviews"] > 0:
        s = starsStr(row["Rating"], row["Number of Reviews"])
        Label(body, text=f"{s}  {round(row['Rating'], 1)}/5  ({int(row['Number of Reviews'])} reviews)",
              font=("Segoe UI", 13), fg=STAR_GOLD, bg=CARD_BG).pack(anchor="w", pady=(0, 12))
    else:
        Label(body, text="No reviews yet.", font=FONT_BODY, fg=TEXT_DK, bg=CARD_BG).pack(anchor="w", pady=(0, 12))

    if reviews:
        outer = Frame(body, bg=CARD_BG)
        outer.pack(fill="both", expand=True)
        canvas = Canvas(outer, bg=CARD_BG, highlightthickness=0)
        sb = Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        inner = Frame(canvas, bg=CARD_BG)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        for rev in reviews:
            rc = Frame(inner, bg="#f8fafc", highlightthickness=1, highlightbackground=BORDER)
            rc.pack(fill="x", pady=4, padx=2)
            Label(rc, text=rev, font=FONT_BODY, fg=TEXT_DK, bg="#f8fafc",
                  anchor="w", wraplength=460, justify="left", padx=12, pady=10).pack(fill="x")
        inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    makeButton(body, "Close", win.destroy, style="ghost").pack(pady=(14, 0))


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
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    listFrame = Frame(canvas, bg=BG)
    canvas.create_window((0, 0), window=listFrame, anchor="nw")
    canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    listFrame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    if not businesses:
        Label(listFrame, text="You haven't added any businesses yet.",
              font=FONT_H2, fg=TEXT_MD, bg=BG, pady=60).pack()
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        flushLayout()
        return

    for biz_name in businesses:
        indexlist = businessDatabase.index[businessDatabase["Name"] == biz_name].tolist()
        if not indexlist:
            continue
        row = businessDatabase.loc[indexlist[0]]

        cardOuter = Frame(listFrame, bg=BORDER)
        cardOuter.pack(padx=16, pady=6, fill="x")
        card = Frame(cardOuter, bg=CARD_BG)
        card.pack(padx=1, pady=1, fill="x")

        # Image
        imgF = Frame(card, bg=CARD_BG, width=92, height=92)
        imgF.pack(side="left", padx=12, pady=12)
        imgF.pack_propagate(False)
        try:
            thumb = Image.open(row["Image"]).resize((88, 88), Image.LANCZOS)
            photo = ImageTk.PhotoImage(thumb)
            lbl = Label(imgF, image=photo, bg=CARD_BG)
            lbl.image = photo
            lbl.pack(expand=True)
        except:
            Label(imgF, text="🏢", font=("Segoe UI", 28), bg="#e2e8f0", fg=TEXT_MD).pack(expand=True, fill="both")

        # Info
        infoF = Frame(card, bg=CARD_BG)
        infoF.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=14)
        Label(infoF, text=row["Name"], font=FONT_CARD, fg=TEXT_DK, bg=CARD_BG, anchor="w").pack(fill="x")
        Label(infoF, text=f"  {row['Category']}  ", font=FONT_SMALL,
              fg=WHITE, bg=PRIMARY, padx=4, pady=2).pack(anchor="w", pady=(5, 3))
        Label(infoF, text="📍 " + row["Location"], font=FONT_SMALL, fg=TEXT_DK, bg=CARD_BG, anchor="w").pack(fill="x")
        if row["Number of Reviews"] > 0:
            s = starsStr(row["Rating"], row["Number of Reviews"])
            Label(infoF, text=f"{s}  {round(row['Rating'],1)}/5  ({int(row['Number of Reviews'])} reviews)",
                  font=("Segoe UI", 10), fg=STAR_GOLD, bg=CARD_BG, anchor="w").pack(fill="x", pady=(5, 0))
        else:
            Label(infoF, text="No reviews yet", font=FONT_SMALL, fg=TEXT_DK, bg=CARD_BG, anchor="w").pack(fill="x", pady=(5, 0))

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
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    flushLayout()


# ============================================================
# CANVAS SCROLL
# ============================================================
def on_frame_configure(event):
    businessViewer.configure(scrollregion=businessViewer.bbox("all"))

# ============================================================
# BUSINESS CARDS
# ============================================================
def starsStr(r, count):
    filled = round(r)
    return "★" * filled + "☆" * (5 - filled)

def _setBg(widget, color):
    try:
        if isinstance(widget, Button): return
        if str(widget.cget("bg")) in (CARD_BG, CARD_HOVER):
            widget.config(bg=color)
        for child in widget.winfo_children():
            _setBg(child, color)
    except: pass

def showBusinesses(df=None):
    for w in businessFrame.winfo_children():
        w.destroy()
    if df is None:
        df = businessDatabase
    if df.empty:
        Label(businessFrame, text="No businesses found.",
              font=FONT_H2, fg=TEXT_LT, bg=BG, pady=60).pack()
        return
    for i, row in df.iterrows():
        cardOuter = Frame(businessFrame, bg=BORDER)
        cardOuter.pack(padx=16, pady=6, fill="x")
        card = Frame(cardOuter, bg=CARD_BG)
        card.pack(padx=1, pady=1, fill="x")

        imgF = Frame(card, bg=CARD_BG, width=92, height=92)
        imgF.pack(side="left", padx=12, pady=12)
        imgF.pack_propagate(False)
        try:
            thumb = Image.open(row["Image"]).resize((88, 88), Image.LANCZOS)
            photo = ImageTk.PhotoImage(thumb)
            lbl = Label(imgF, image=photo, bg=CARD_BG)
            lbl.image = photo
            lbl.pack(expand=True)
        except:
            Label(imgF, text="🏢", font=("Segoe UI", 28), bg="#e2e8f0", fg=TEXT_MD).pack(expand=True, fill="both")

        infoF = Frame(card, bg=CARD_BG)
        infoF.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=14)
        Label(infoF, text=row["Name"], font=FONT_CARD, fg=TEXT_DK, bg=CARD_BG, anchor="w").pack(fill="x")
        Label(infoF, text=f"  {row['Category']}  ", font=FONT_SMALL,
              fg=WHITE, bg=PRIMARY, padx=4, pady=2).pack(anchor="w", pady=(5, 3))
        Label(infoF, text="📍 " + row["Location"], font=FONT_SMALL, fg=TEXT_DK, bg=CARD_BG, anchor="w").pack(fill="x")
        if row["Number of Reviews"] > 0:
            s = starsStr(row["Rating"], row["Number of Reviews"])
            Label(infoF, text=f"{s}  {round(row['Rating'],1)}/5  ({int(row['Number of Reviews'])} reviews)",
                  font=("Segoe UI", 10), fg=STAR_GOLD, bg=CARD_BG, anchor="w").pack(fill="x", pady=(5, 0))
        else:
            Label(infoF, text="No reviews yet", font=FONT_SMALL, fg=TEXT_DK, bg=CARD_BG, anchor="w").pack(fill="x", pady=(5, 0))

        btnF = Frame(card, bg=CARD_BG)
        btnF.pack(side="right", padx=20, pady=14)
        makeButton(btnF, "View Details", lambda r=row: showDetails(r), style="blac").pack(pady=(0, 6), fill="x")
        makeButton(btnF, "Add Review",   lambda r=row: addReviewScreen(r), style="ghost").pack(fill="x")

        card.bind("<Enter>", lambda e, c=card: (_setBg(c, CARD_HOVER), c.config(bg=CARD_HOVER)))
        card.bind("<Leave>", lambda e, c=card: (_setBg(c, CARD_BG),    c.config(bg=CARD_BG)))
    businessFrame.update_idletasks()
    businessViewer.configure(scrollregion=businessViewer.bbox("all"))
    flushLayout()

# ============================================================
# DETAIL WINDOW
# ============================================================
def showDetails(business):
    win = Toplevel(startScreen)
    win.title(business["Name"])
    win.configure(bg=BG)
    win.resizable(False, False)
    win.grab_set()

    hdr = Frame(win, bg=HEADER_BG)
    hdr.pack(fill="x")
    Label(hdr, text=business["Name"], font=FONT_H1, fg=WHITE, bg=HEADER_BG, pady=14, padx=20).pack(anchor="w")

    body = Frame(win, bg=BG, padx=28, pady=18)
    body.pack(fill="both", expand=True)

    try:
        img = Image.open(business["Image"])
        img.thumbnail((380, 260), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        lbl = Label(body, image=photo, bg=BG)
        lbl.image = photo
        lbl.pack(pady=(0, 14))
    except:
        Label(body, text="[No Image]", font=FONT_BODY, fg=TEXT_MD, bg=BG).pack(pady=(0, 14))

    for label, value in [("Location", business["Location"]),
                         ("Category", business["Category"]),
                         ("Description", business["Description"])]:
        rowF = Frame(body, bg=BG)
        rowF.pack(fill="x", pady=4)
        Label(rowF, text=f"{label}:", font=("Segoe UI", 11, "bold"), fg=TEXT_DK, bg=BG, width=13, anchor="w").pack(side="left")
        Label(rowF, text=value, font=FONT_BODY, fg=TEXT_DK, bg=BG, anchor="w", wraplength=340).pack(side="left")

    if business["Number of Reviews"] > 0:
        s = starsStr(business["Rating"], business["Number of Reviews"])
        Label(body, text=f"{s}  {round(business['Rating'],1)} / 5.0",
              font=("Segoe UI", 15), fg=STAR_GOLD, bg=BG).pack(pady=(10, 4))

    reviews = business["Reviews"] if isinstance(business["Reviews"], list) else []
    if reviews:
        Label(body, text="Customer Reviews", font=FONT_H2, fg=TEXT_DK, bg=BG).pack(anchor="w", pady=(12, 6))
        revOuter = Frame(body, bg=BG)
        revOuter.pack(fill="x")
        revCanvas = Canvas(revOuter, bg=BG, height=130, highlightthickness=0)
        revScroll = Scrollbar(revOuter, orient="vertical", command=revCanvas.yview)
        revCanvas.configure(yscrollcommand=revScroll.set)
        revCanvas.pack(side="left", fill="both", expand=True)
        revScroll.pack(side="right", fill="y")
        revFrame = Frame(revCanvas, bg=BG)
        revCanvas.create_window((0, 0), window=revFrame, anchor="nw")
        for rev in reviews:
            rc = Frame(revFrame, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
            rc.pack(fill="x", pady=3, padx=2)
            Label(rc, text=rev, font=FONT_SMALL, fg=TEXT_DK, bg=CARD_BG,
                  anchor="w", wraplength=360, justify="left", padx=10, pady=6).pack(fill="x")
        revFrame.update_idletasks()
        revCanvas.configure(scrollregion=revCanvas.bbox("all"))

    makeButton(body, "Close", win.destroy, style="ghost").pack(pady=(16, 0))

# ============================================================
# HOME SCREEN
# ============================================================
def setHomeScreen():
    clearScreen()
    global accountInUse
    # Show appropriate toolbar
    if accountDatabase.loc[accountInUse, "Type"] == "Owner":
        showToolbar()
    else:
        showCustomerToolbar()

    # Search banner
    searchFrame.pack(fill="x")
    searchLabel.pack(side="left", padx=(16, 6), pady=10)
    searchEntry.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=10)
    chooseCategory.pack(side="left", padx=(0, 6), pady=10)
    ratingOrderInput.pack(side="left", padx=(0, 6), pady=10)
    goButton.pack(side="left", padx=(0, 16), pady=10)

    # Scrollbar must be packed before canvas
    viewerScrollbar.pack(side="right", fill="y")
    businessViewer.pack(side="left", fill="both", expand=True)
    showBusinesses()
    flushLayout()

def sortAndSearch():
    query = searchVar.get().lower()
    category = chosenCategory.get()
    rating_sort = ratingOrder.get()
    filtered = businessDatabase.copy()
    if query:
        filtered = filtered[filtered.apply(
            lambda row: query in row["Name"].lower() or query in row["Description"].lower(), axis=1)]
    if category != "Sort by Category":
        filtered = filtered[filtered["Category"] == category]
    if rating_sort == "Highest to Lowest Rating":
        filtered = filtered.sort_values(by="Rating", ascending=False)
    elif rating_sort == "Lowest to Highest Rating":
        filtered = filtered.sort_values(by="Rating", ascending=True)
    showBusinesses(filtered)

# ============================================================
# REVIEW SCREEN
# ============================================================
def addReviewScreen(business):
    global starButtons, rating
    rating.set(0)
    starButtons = []
    win = Toplevel(startScreen)
    win.title("Review — " + business["Name"])
    win.configure(bg=BG)
    win.resizable(False, False)
    win.grab_set()

    hdr = Frame(win, bg=HEADER_BG)
    hdr.pack(fill="x")
    Label(hdr, text=f"Review: {business['Name']}", font=FONT_H1,
          fg=WHITE, bg=HEADER_BG, pady=14, padx=20).pack(anchor="w")

    body = Frame(win, bg=BG, padx=28, pady=20)
    body.pack(fill="both", expand=True)

    Label(body, text="Rate your experience", font=FONT_H2, fg=TEXT_DK, bg=BG).pack(pady=(0, 8))
    starFrame = Frame(body, bg=BG)
    starFrame.pack(pady=(0, 14))
    for i in range(5):
        star = Button(starFrame, text="☆", font=("Segoe UI", 28),
                      fg="black", bg=BG, activebackground=BG, activeforeground="red",
                      relief="flat", cursor="hand2", bd=0, command=lambda i=i: setRating(i + 1))
        star.bind("<Enter>", lambda e, s=star: s.config(fg="red"))
        star.bind("<Leave>", lambda e, s=star: s.config(fg="black"))
        star.pack(side="left", padx=4)
        starButtons.append(star)

    Label(body, text="Tell others about your experience:",
          font=FONT_BODY, fg=TEXT_DK, bg=BG).pack(anchor="w", pady=(0, 6))
    reviewDescription = Text(win, height=6, width=46, wrap="word",
                             font=FONT_BODY, fg=TEXT_DK, bg=INPUT_BG,
                             insertbackground=TEXT_DK, relief="flat",
                             highlightthickness=1, highlightbackground=INPUT_BD,
                             highlightcolor=PRIMARY, bd=0, padx=8, pady=6)
    reviewDescription.pack(in_=body, fill="x")
    addTextPlaceholder(reviewDescription, "Describe your experience here…")
    makeButton(body, "Submit Review",
               lambda: [updateReview(business, reviewDescription.get("1.0", "end-1c")), win.destroy()],
               style="primary").pack(pady=(16, 0))

def setRating(value):
    global rating
    rating.set(value)
    updateStars()

def updateStars():
    global starButtons, rating
    for i in range(5):
        starButtons[i].config(text="★" if i < rating.get() else "☆")

def updateReview(row, review):
    global rating, accountInUse, reviewsDatabase
    review = review.strip()
    if review in ("", "Describe your experience here…"):
        return
    if not isinstance(accountDatabase.loc[accountInUse, "Reviews"], list):
        accountDatabase.loc[accountInUse, "Reviews"] = []
    index = businessDatabase.index[businessDatabase["Name"] == row["Name"]].tolist()[0]
    username = accountDatabase.loc[accountInUse, "Username"] if accountInUse >= 0 else ""
    reviewsDatabase.loc[len(reviewsDatabase)] = [row["Name"], username, int(rating.get()), review]
    accountDatabase.loc[accountInUse, "Reviews"].append({"rating": rating.get(), "review": review})
    accountDatabase.loc[accountInUse, "Number of Reviews"] += 1
    refreshBusinessReviewsFromTable()
    saveData()
    setHomeScreen()

def saveData():
    accountDatabase.to_csv(ACCOUNTS_CSV, index=False)
    businessDatabase.to_csv(BUSINESSES_CSV, index=False)
    reviewsDatabase.to_csv(REVIEWS_CSV, index=False)

# ============================================================
# MAIN WINDOW
# ============================================================
startScreen = Tk()
startScreen.title("CityPulse")
startScreen.state("zoomed")
startScreen.configure(bg=HEADER_BG)

applyStyles()

accountInUse     = -1
filePath         = ""
currentBusinessIndex = -1
rating           = IntVar(value=0)
starButtons      = []

# ── Data ────────────────────────────────────────────────────
def _parseList(x):
    if isinstance(x, list): return x
    if pd.isna(x): return []
    try:
        parsed = ast.literal_eval(str(x).strip())
        return parsed if isinstance(parsed, list) else []
    except: return []

if os.path.exists(ACCOUNTS_CSV):
    accountDatabase = pd.read_csv(ACCOUNTS_CSV)
    accountDatabase["Businesses"] = accountDatabase["Businesses"].apply(_parseList)
    accountDatabase["Reviews"]    = accountDatabase["Reviews"].apply(_parseList)
else:
    accountDatabase = pd.DataFrame(columns=["Username","Password","Email","Number of Reviews","Certificates","Reviews","Type","Businesses"])

if os.path.exists(BUSINESSES_CSV):
    businessDatabase = pd.read_csv(BUSINESSES_CSV)
    businessDatabase["Reviews"] = businessDatabase["Reviews"].apply(_parseList)
else:
    businessDatabase = pd.DataFrame(columns=["Name","Location","Image","Description","Category","Rating","Number of Reviews","Total Rating Count","Reviews"])

if os.path.exists(REVIEWS_CSV):
    reviewsDatabase = pd.read_csv(REVIEWS_CSV)
else:
    reviewsDatabase = pd.DataFrame(columns=["Business Name", "Username", "Rating", "Review"])
    # One-time migration from legacy business-level Reviews list into reviews.csv
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

for col in ["Business Name", "Username", "Rating", "Review"]:
    if col not in reviewsDatabase.columns:
        reviewsDatabase[col] = "" if col in ("Business Name", "Username", "Review") else 0

def refreshBusinessReviewsFromTable():
    # Rebuild business review stats/text from the dedicated reviews table.
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
        businessDatabase.loc[idx, "Rating"] = (total / count) if count > 0 else 0.0
        businessDatabase.at[idx, "Reviews"] = [
            f"{int(r)}★ - {str(t).strip()}"
            for r, t in zip(ratings.tolist(), subset["Review"].fillna("").tolist())
        ]

refreshBusinessReviewsFromTable()

# ── Permanent header ─────────────────────────────────────────
headerFrame = Frame(startScreen, bg=HEADER_BG, height=64)
headerFrame.pack(fill="x", side="top")
headerFrame.pack_propagate(False)
Label(headerFrame, text="🏙  CityPulse", font=FONT_TITLE,
      fg=WHITE, bg=HEADER_BG, padx=24).pack(side="left", fill="y")

# ── Owner toolbar (shown after login, hidden on auth) ────────
toolbar = Frame(startScreen, bg=TOOLBAR_BG)
# (packed/unpacked by showToolbar / hideToolbar)

# ── Main content area ────────────────────────────────────────
mainContent = Frame(startScreen, bg=BG)
mainContent.pack(fill="both", expand=True)

# ── Auth widgets ─────────────────────────────────────────────
authWrapper = Frame(mainContent, bg=BG)
authCard = Frame(authWrapper, bg=CARD_BG, padx=52, pady=44,
                 highlightthickness=1, highlightbackground=BORDER)
authCard.pack(padx=20, pady=50)

Label(authCard, text="🏙", font=("Segoe UI", 36), fg=PRIMARY, bg=CARD_BG).pack(pady=(0, 6))
Label(authCard, text="Welcome to CityPulse", font=("Segoe UI", 18, "bold"), fg=TEXT_DK, bg=CARD_BG).pack(pady=(0, 4))
Label(authCard, text="Discover and review local businesses",
      font=FONT_BODY, fg=TEXT_DK, bg=CARD_BG).pack(pady=(0, 26))

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

# Show initial auth screen
authWrapper.pack(fill="both", expand=True)
createNewAccountButton.pack(pady=(0, 8))
loginButton.pack()

# ── Business form widgets (children of mainContent) ──────────
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

# ── Edit business widgets ────────────────────────────────────
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

# ── Business canvas + scrollbar ─────────────────────────────
businessViewer  = Canvas(mainContent, bg=BG, highlightthickness=0)
viewerScrollbar = Scrollbar(mainContent, orient="vertical", command=businessViewer.yview)
businessViewer.configure(yscrollcommand=viewerScrollbar.set)
businessFrame = Frame(businessViewer, bg=BG)
businessViewer.create_window((0, 0), window=businessFrame, anchor="nw")
businessFrame.bind("<Configure>", on_frame_configure)
businessViewer.bind("<MouseWheel>", lambda e: businessViewer.yview_scroll(int(-1*(e.delta/120)), "units"))

# ── Search bar (child of mainContent) ────────────────────────
searchFrame = Frame(mainContent, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER)
searchLabel = Label(searchFrame, text="🔍  Search:", font=FONT_BTN, fg=TEXT_DK, bg=CARD_BG)
searchVar   = StringVar()
searchEntry = Entry(searchFrame, textvariable=searchVar, font=FONT_BODY,
                    bg=INPUT_BG, fg=TEXT_DK, relief="flat",
                    highlightthickness=1, highlightbackground=INPUT_BD,
                    highlightcolor=PRIMARY, bd=0, width=26, insertbackground=TEXT_DK)
searchEntry.bind("<Return>", lambda e: sortAndSearch())

chosenCategory = StringVar()
chooseCategory = ttk.Combobox(searchFrame,
    values=["Food","Service","Retail","Health & Wellness","Education",
            "Automotive","Travel & Hospitality","Entertainment","Home Services"],
    textvariable=chosenCategory, state="readonly", width=18, font=FONT_BODY)
chooseCategory.set("Sort by Category")

ratingOrder = StringVar()
ratingOrderInput = ttk.Combobox(searchFrame,
    values=["Highest to Lowest Rating","Lowest to Highest Rating"],
    textvariable=ratingOrder, state="readonly", width=22, font=FONT_BODY)
ratingOrderInput.set("Sort by Rating")

goButton = makeButton(searchFrame, "Search", sortAndSearch, style="primary")

# ── Launch ───────────────────────────────────────────────────
startScreen.mainloop()
