#import all libraries and external sources
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
from PIL import Image, ImageTk
import os
import ast

#loading screen
def loginScreen():
    usernameInput.pack()
    passwordInput.pack()
    emailInput.pack_forget()
    startText.pack_forget()
    loginCompletedButton.pack()
    createAccountCompletedButton.pack_forget()
    startText.pack()
def newAccountScreen():
    usernameInput.pack()
    emailInput.pack()
    passwordInput.pack()
    startText.pack_forget()
    createAccountCompletedButton.pack()
    loginCompletedButton.pack_forget()
    startText.pack()
def login(username, password):
    index = accountDatabase.index[accountDatabase['Username']==username].tolist()
    if not index:
        startText.config(text = 'Account Not Found')
    elif accountDatabase.loc[index[0], 'Password'] != password:
        startText.config(text = 'Incorrect Password')
    else:
        global accountInUse
        accountInUse = index[0]
        setHomeScreen()
def createAccount(username, password, email, type):
    index = accountDatabase.index[accountDatabase['Username']==username].tolist()
    if index:
        startText.config(text = 'Username is Unavailable')
    else:
        global accountInUse
        accountInUse = len(accountDatabase)
        accountDatabase.loc[len(accountDatabase)] = [username, password, email, 0, [], [], type, []]
        saveData()
        setHomeScreen()
def showMenu():
    menuBar.delete(0, 'end')
    fileMenu = Menu(menuBar, tearoff =0)
    fileMenu.add_command(label = "Log Out", command = lambda:logOut())
    fileMenu.add_command(label = "Exit", command = lambda:startScreen.quit())
    menuBar.add_cascade(label = "Account", menu = fileMenu)
    startScreen.config(menu = menuBar)
    global accountInUse
    if accountDatabase.loc[accountInUse, 'Type'] == 'Owner':
        manageMenu = Menu(menuBar, tearoff = 0)
        manageMenu.add_command(label = "Add Business", command=addBusinessScreen)
        if isinstance(accountDatabase.loc[accountInUse, 'Businesses'],list) and accountDatabase.loc[accountInUse, 'Businesses']:
            editMenu = Menu(manageMenu, tearoff=0)
            for item in accountDatabase.loc[accountInUse, 'Businesses']:
                editMenu.add_command(label = item, command = lambda i=item:editBusiness(i))
            manageMenu.add_cascade(label = 'Edit', menu = editMenu)
        menuBar.add_cascade(label = "Manage", menu = manageMenu)
def logOut():
    createNewAccountButton.pack()
    loginButton.pack()
    usernameInput.delete(0, END)
    passwordInput.delete(0, END)
    emailInput.delete(0, END)
    usernameInput.insert(0, 'Enter Username')
    passwordInput.insert(0,'Enter Password')
    emailInput.insert(0,'Enter Email')
    usernameInput.config(fg = 'grey')
    passwordInput.config(fg = 'grey')
    emailInput.config(fg = 'grey')
    global accountInUse
    accountInUse = -1
    startScreen.config(menu = None)
def accountType():
    if usernameInput.get() == "Enter Username" or usernameInput.get() == "":
        startText.config(text = "Enter a valid username")
    elif emailInput.get() == "Enter Email" or emailInput.get() == "":
        startText.config(text = "Enter a valid email")
    elif passwordInput.get() == "Enter Password" or passwordInput.get() == "":
        startText.config(text = "Enter a valid password")
    else:
        global accountInUse
        clearScreen()
        startText.pack()
        startText.config(text = "I am a...")
        customerButton.pack()
        ownerButton.pack()
def uploadFile():
    global filePath
    filePath = filedialog.askopenfilename()
    if filePath:
        businessImageInput.config(bg = 'green')
        createBusinessText.config(text = "File Path: " + filePath)
    else:
        createBusinessText.config(text = "No file selected")
def addBusinessScreen():
    clearScreen()
    businessDescriptionInput.delete(0, END)
    businessLocationInput.delete(0, END)
    businessNameInput.delete(0, END)
    businessNameInput.insert(0, 'Business Name')
    businessLocationInput.insert(0,'Business Location')
    businessDescriptionInput.insert(0,'Business Description')
    businessDescriptionInput.config(fg = 'grey')
    businessNameInput.config(fg = 'grey')
    businessLocationInput.config(fg = 'grey')
    createBusinessTitle.pack()
    businessNameInput.pack()
    businessCategoryInput.pack()
    businessLocationInput.pack()
    businessDescriptionInput.pack()
    businessImageInput.pack()
    createBusinessButton.pack()
    createBusinessText.pack()
def addPlaceholder(entry, placeholderText):
    entry.insert(0, placeholderText)
    entry.config(fg = 'grey')
    def on_focus_in(event):
        if entry.get() == placeholderText:
            entry.delete(0, END)
            entry.config(fg = 'black')
    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholderText)
            entry.config(fg = 'grey')
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
def createBusiness(name, location, description):
    businessImageInput.config(bg = 'SystemButtonFace')
    index = businessDatabase.index[businessDatabase['Name']==name].tolist()
    global filePath
    global accountInUse
    if index:
        createBusinessText.config(text = 'Business is Already Created')
    elif businessNameInput.get()=="Business Name":
        createBusinessText.config(text = "Enter valid name")
    elif businessLocationInput.get()=="Business Location":
        createBusinessText.config(text = "Enter valid location")
    elif selectedCategory.get() == "Select Category":
        createBusinessText.config(text = "Select a category")
    elif businessDescriptionInput.get()=="Business Description":
        createBusinessText.config(text = "Enter valid description")
    elif not filePath:
        createBusinessText.config(text = "Upload Image")
    else:
        businessDatabase.loc[len(businessDatabase)] = [name, location, filePath, description, selectedCategory.get(), 0.0, 0, 0, []]
        if not isinstance(accountDatabase.at[accountInUse, 'Businesses'], list):
            accountDatabase.at[accountInUse, 'Businesses'] = []
        accountDatabase.at[accountInUse, 'Businesses'].append(name)
        saveData()
        setHomeScreen()
        filePath = ""
        createBusinessText.config(text = "")
        businessCategoryInput.set("Select Category")
def updateBusiness(updatedValue, type, index):
    if type == "Name":
        businessDatabase.loc[index, "Name"] = updatedValue
    if type == "Location":
        businessDatabase.loc[index, "Location"] = updatedValue
    if type == "Description":
        businessDatabase.loc[index, "Description"] = updatedValue
    if type == "Category":
        businessDatabase.loc[index, "Category"] = updatedValue
    if type == "Image":
        businessDatabase.loc[index, "Image"] = updatedValue
def editBusiness(item):
    clearScreen()
    global currentBusinessIndex
    indexlist = businessDatabase.index[businessDatabase['Name']==item].tolist()
    if not indexlist:
        return
    currentBusinessIndex = indexlist[0]
    editBusinessNameInput.delete(0, END)
    editBusinessNameInput.insert(0, businessDatabase.loc[currentBusinessIndex, "Name"])
    editBusinessLocationInput.delete(0, END)
    editBusinessLocationInput.insert(0, businessDatabase.loc[currentBusinessIndex, "Location"])
    editBusinessDescriptionInput.delete(0, END)
    editBusinessDescriptionInput.insert(0, businessDatabase.loc[currentBusinessIndex, "Description"])
    editSelectedCategory.insert(0, businessDatabase.loc[currentBusinessIndex, "Category"])
    editBusinessNameInput.pack()
    editBusinessLocationInput.pack()
    editBusinessCategoryInput.pack()
    editBusinessDescriptionInput.pack()
    editBusinessImageInput.pack()
    editBusinessButton.pack()
def finalizeEdits():
    global currentBusinessIndex
    global filePath
    index = currentBusinessIndex
    if editBusinessNameInput.get() != "" and editBusinessNameInput.get() != "Business Name" :
        updateBusiness(editBusinessNameInput.get(), "Name", index)
    if editBusinessLocationInput.get() != "" and editBusinessLocationInput.get() != "Business Location" :
        updateBusiness(editBusinessLocationInput.get(), "Location", index)
    if editBusinessDescriptionInput.get() != "" and editBusinessDescriptionInput.get() != "Business Description" :
        updateBusiness(editBusinessDescriptionInput.get(), "Description", index)
    if editSelectedCategory.get() != "Select Category":
        updateBusiness(editSelectedCategory.get(), "Category", index)
    if filePath:
        updateBusiness(filePath, "Image", index)
        filePath = ""
    setHomeScreen()
def clearScreen():
    for widget in startScreen.winfo_children():
        widget.pack_forget()
    titleText.pack()
def on_frame_configure(event):
    businessViewer.configure(scrollregion=businessViewer.bbox("all"))
def showBusinesses(df=None):
    imageRefs = []
    for widget in businessFrame.winfo_children():
        widget.destroy()
    if df is None:
        df = businessDatabase
    for i, row in df.iterrows():
        businessCard = Frame(businessFrame, bd =1, relief ="solid")
        businessCard.pack(padx=10,pady=5, fill = "x")
        try:
            thumbnail = Image.open(row['Image'])
            thumbnail = thumbnail.resize((80,80))
            thumbnailphoto = ImageTk.PhotoImage(thumbnail)
            thumbnailLabel = Label(businessCard, image = thumbnailphoto)
            thumbnailLabel.image = thumbnailphoto
            thumbnailLabel.pack(side="left", padx =5, pady=5)
            imageRefs.append(thumbnailphoto)
        except:
            Label(businessCard, text = "[No Image]", width =10, height =5 ).pack(side="left", padx=5, pady=5)
        businessLabel = Label(businessCard, text = row['Name'])
        businessLabel.pack(side="left", padx=10,pady=5)
        businessButton = Button(businessCard, text = "View Details", command = lambda r =row:showDetails(r))
        businessButton.pack(side="right", padx=10)
        if(row['Number of Reviews']) > 0:
            reviewLabel = Label(businessCard, text = str(round(row['Rating'], 1)) + " Stars")
            reviewLabel.pack(side = "left", padx=10)
        reviewButton = Button(businessCard, text = "Add Review", command = lambda r =row:addReviewScreen(r))
        reviewButton.pack(side="right", padx=10)
        def on_enter(e, w=businessCard):
            w.config(bg="lightblue")
        def on_leave(e, w = businessCard):
            w.config(bg="SystemButtonFace")
        businessCard.bind("<Enter>", on_enter)
        businessCard.bind("<Leave>", on_leave)
def showDetails(business):
    detailWindow = Toplevel(startScreen)
    detailWindow.title(business['Name'])
    Label(detailWindow, text= "Name: "+ business['Name']).pack(padx=10,pady=5)
    Label(detailWindow, text = "Location: "+business['Location']).pack(padx=10,pady=5)
    Label(detailWindow, text = "Category: " + business['Category']).pack(padx=10,pady=5)
    Label(detailWindow, text = "Description: " + business['Description']).pack(padx=10,pady=5)
    businessImg = Image.open((business['Image']))
    maxThumbnailWidth, maxThumbnailHeight =400,400
    businessImg.thumbnail((maxThumbnailWidth, maxThumbnailHeight))   
    businessPhoto = ImageTk.PhotoImage(businessImg)  
    businessImageLabel = Label(detailWindow, image = businessPhoto)  
    businessImageLabel.image = businessPhoto
    businessImageLabel.pack(padx=10, pady=10)
    reviewsText = "Reviews:\n"
    if isinstance(business['Reviews'], list):
        for review in business['Reviews']:
            reviewsText += review +"\n"
    reviewLabel = Label(detailWindow, text = reviewsText)
    reviewLabel.pack()
def setHomeScreen():
    clearScreen()
    showMenu()
    titleText.pack(side="top", pady=10)
    searchFrame.pack(side = "top",fill="x", padx=10, pady=5)
    searchLabel.pack(side="left", padx=(0,5))
    searchEntry.pack(side="left", fill ="x", expand = True, padx=(0,5))
    chooseCategory.pack(side = "left", padx=(5,5))
    ratingOrderInput.pack(side="left", padx=(5,5))
    goButton.pack(side="left")
    businessViewer.pack(side = "left", fill ="both", expand = True)
    viewerScrollbar.pack(side = "right", fill = "y")
    showBusinesses()
def addReviewScreen(business):
    global starButtons
    global rating
    rating.set(0)
    starButtons = []
    reviewWindow = Toplevel(startScreen)
    reviewWindow.title(business['Name'])
    Label(reviewWindow, text = "Leave a review and share your experience at " + business['Name'] + "!").pack()
    starFrame = Frame(reviewWindow)
    starFrame.pack(pady=10)
    for i in range(5):
        star = Button(starFrame, text = "☆", command = lambda i=i:setRating(i+1))
        star.pack(side="left")
        starButtons.append(star)
    reviewDescription = Text(reviewWindow, height =5, width = 40, wrap="word")
    reviewDescription.pack(fill="x")
    addTextPlaceholder(reviewDescription, "Describe Experience Here")
    submitReviewButton= Button(reviewWindow, text = "Submit Review", command = lambda:[updateReview(business, reviewDescription.get("1.0", "end-1c")), reviewWindow.destroy()] )
    submitReviewButton.pack(pady=10)
def setRating(value):
    global rating
    rating.set(value)
    updateStars()
def updateStars():
    global starButtons
    global rating
    for i in range(5):
        if i<rating.get():
            starButtons[i].config(text = "★")
        else:
            starButtons[i].config(text = "☆")
def updateReview(row, review):
    global rating
    global accountInUse
    review = review.strip()
    if review == "" or review == "Describe Experience Here":
        return
    if not isinstance(accountDatabase.loc[accountInUse, 'Reviews'], list):
        accountDatabase.loc[accountInUse, 'Reviews'] = []
    index = businessDatabase.index[businessDatabase['Name']==row['Name']].tolist()[0]
    accountDatabase.loc[accountInUse, 'Reviews'].append({"rating": rating.get(), "review":review})
    accountDatabase.loc[accountInUse, "Number of Reviews"]+= 1
    businessDatabase.loc[index, 'Number of Reviews'] +=1
    businessDatabase.loc[index, 'Total Rating Count'] += rating.get()
    if not isinstance(businessDatabase.loc[index, "Reviews"], list):
        businessDatabase.loc[index, "Reviews"] = []
    businessDatabase.loc[index, "Rating"] = businessDatabase.loc[index, 'Total Rating Count']/businessDatabase.loc[index, 'Number of Reviews']
    businessDatabase.loc[index, "Reviews"].append(f"{rating.get()}★ - {review.strip()}")
    setHomeScreen()
def addTextPlaceholder(text_widget, placeholder):
    text_widget.insert("1.0", placeholder)
    text_widget.config(fg = "grey")
    def on_focus_in(event):
        if text_widget.get("1.0", "end-1c") == placeholder:
            text_widget.delete("1.0", END)
            text_widget.config(fg = "black")
    def on_focus_out(event):
        if text_widget.get("1.0", "end-1c") == "":
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg = "grey")
    text_widget.bind("<FocusIn>", on_focus_in)
    text_widget.bind("<FocusOut>", on_focus_out)
def sortAndSearch():
    query = searchVar.get().lower()
    category = chosenCategory.get()
    rating_sort = ratingOrder.get()
    filtered = businessDatabase.copy()
    if query and query!="":
        filtered = filtered[filtered.apply(lambda row: query in row['Name'].lower() or query in row['Description'].lower(), axis=1)]
    if category != "t by Category":
        filtered = filtered[filtered['Category']==category]
    if rating_sort == "Highest to Lowest Rating":
        filtered = filtered.sort_values(by = "Rating", ascending = False)
    elif rating_sort == "Lowest to Highest Rating":
        filtered = filtered.sort_values(by = "Rating", ascending = True)
    showBusinesses(filtered)
def saveData(): 
    accountDatabase.to_csv("accounts.csv", index=False)
    businessDatabase.to_csv("businesses.csv", index = False)
startScreen = Tk()
accountInUse = -1
menuBar = Menu(startScreen)
startScreen.title("CityPulse")
startScreen.state('zoomed')
titleText = Label(startScreen, text = 'CityPulse')
titleText.pack()
filePath = ""
startText = Label(startScreen, text = '')
if os.path.exists("accounts.csv"):
    accountDatabase = pd.read_csv("accounts.csv")
    accountDatabase['Businesses'] = accountDatabase['Businesses'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else[])
    accountDatabase['Reviews'] = accountDatabase['Reviews'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
else:
    accountDatabase = pd.DataFrame(columns= ['Username', 'Password', 'Email', 'Number of Reviews', 'Certificates', 'Reviews', 'Type', 'Businesses'])
if os.path.exists("businesses.csv"):
    businessDatabase = pd.read_csv("businesses.csv")
    businessDatabase['Reviews'] = businessDatabase['Reviews'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else[])
else:
    businessDatabase = pd.DataFrame(columns = ['Name', 'Location', 'Image', 'Description', 'Category', 'Rating', 'Number of Reviews', 'Total Rating Count', 'Reviews'])
createNewAccountButton = Button(startScreen, text = 'Create New Account', command = newAccountScreen)
loginButton = Button(startScreen, text = 'Login Into Existing Account', command = loginScreen)
createNewAccountButton.pack()
loginButton.pack()
usernameInput = Entry(startScreen)
addPlaceholder(usernameInput, "Enter Username")
passwordInput = Entry(startScreen)
addPlaceholder(passwordInput, "Enter Password")
emailInput = Entry(startScreen)
addPlaceholder(emailInput, "Enter Email")
loginCompletedButton = Button(startScreen, text = 'Login', command = lambda:login(usernameInput.get(), passwordInput.get()))
createAccountCompletedButton = Button(startScreen, text = 'Create New Account', command = lambda:accountType())
customerButton = Button(startScreen, text = "Customer", command= lambda:createAccount(usernameInput.get(), passwordInput.get(), emailInput.get(), "Customer"))
ownerButton = Button(startScreen, text = "Owner", command = lambda:createAccount(usernameInput.get(), passwordInput.get(), emailInput.get(), "Owner"))
businessNameInput = Entry(startScreen)
addPlaceholder(businessNameInput, "Business Name")
businessLocationInput = Entry(startScreen)
addPlaceholder(businessLocationInput, "Business Location")
selectedCategory = StringVar()
businessCategoryInput = ttk.Combobox(startScreen, values = ['Food', 'Service', 'Retail', 'Health & Wellness', 'Education', 'Automotive', 'Travel & Hospitality', 'Entertainment', 'Home Services'], textvariable = selectedCategory, state="readonly")
businessCategoryInput.set("Select Category")
businessDescriptionInput = Entry(startScreen)
addPlaceholder(businessDescriptionInput, "Business Description")
businessImageInput = Button(startScreen, text = "Upload Business Image", command = uploadFile)
createBusinessButton = Button(startScreen, text = "Create Business", command = lambda:createBusiness(businessNameInput.get(), businessLocationInput.get(), businessDescriptionInput.get()))
createBusinessText = Label(startScreen)
createBusinessTitle = Label(startScreen,text = "Create your business!")
editBusinessNameInput = Entry(startScreen)
addPlaceholder(editBusinessNameInput, "Business Name")
editBusinessLocationInput = Entry(startScreen)
addPlaceholder(editBusinessLocationInput, "Business Location")
editSelectedCategory = StringVar()
editBusinessCategoryInput = ttk.Combobox(startScreen, values = ['Food', 'Service', 'Retail', 'Health & Wellness', 'Education', 'Automotive', 'Travel & Hospitality', 'Entertainment', 'Home Services'], textvariable = editSelectedCategory, state="readonly")
editBusinessCategoryInput.set("Select Category")
editBusinessDescriptionInput = Entry(startScreen)
addPlaceholder(editBusinessDescriptionInput, "Business Description")
editBusinessImageInput = Button(startScreen, text = "Upload Business Image", command = uploadFile)
editBusinessButton = Button(startScreen, text = "Finalize Changes", command = lambda:finalizeEdits())
editBusinessText = Label(startScreen)
homeButton = Button(startScreen, command = lambda:clearScreen())
currentBusinessIndex = -1
businessViewer = Canvas(startScreen)
viewerScrollbar = Scrollbar(startScreen, orient = "vertical", command = businessViewer.yview)
businessViewer.configure(yscrollcommand=viewerScrollbar.set)
businessFrame = Frame(businessViewer)
businessViewer.create_window((0,0), window = businessFrame, anchor = "nw")
businessFrame.bind("<Configure>", on_frame_configure)
rating = IntVar(value = 0)
starButtons = []
searchFrame = Frame(startScreen)
searchLabel = Label(searchFrame, text = "Search:")
searchVar = StringVar()
searchEntry = Entry(searchFrame, textvariable = searchVar)
searchEntry.bind("<Return>", lambda e: sortAndSearch())
chosenCategory = StringVar()
chooseCategory = ttk.Combobox(searchFrame, values = ['Food', 'Service', 'Retail', 'Health & Wellness', 'Education', 'Automotive', 'Travel & Hospitality', 'Entertainment', 'Home Services'], textvariable = chosenCategory, state = "readonly")
chooseCategory.set("Sort by Category")
ratingOrder = StringVar()
ratingOrderInput = ttk.Combobox(searchFrame, values = ['Highest to Lowest Rating', 'Lowest to Highest Rating'], textvariable= ratingOrder, state = 'readonly')
ratingOrderInput.set("Sort by Rating")
goButton = Button(searchFrame, text = "Sort and Search", command = lambda:sortAndSearch())
startScreen.mainloop()

#import all libraries and external sources
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
from PIL import Image, ImageTk
import os
import ast

#loading screen
def loginScreen():
    usernameInput.pack()
    passwordInput.pack()
    emailInput.pack_forget()
    startText.pack_forget()
    loginCompletedButton.pack()
    createAccountCompletedButton.pack_forget()
    startText.pack()
def newAccountScreen():
    usernameInput.pack()
    emailInput.pack()
    passwordInput.pack()
    startText.pack_forget()
    createAccountCompletedButton.pack()
    loginCompletedButton.pack_forget()
    startText.pack()
def login(username, password):
    index = accountDatabase.index[accountDatabase['Username']==username].tolist()
    if not index:
        startText.config(text = 'Account Not Found')
    elif accountDatabase.loc[index[0], 'Password'] != password:
        startText.config(text = 'Incorrect Password')
    else:
        global accountInUse
        accountInUse = index[0]
        setHomeScreen()
def createAccount(username, password, email, type):
    index = accountDatabase.index[accountDatabase['Username']==username].tolist()
    if index:
        startText.config(text = 'Username is Unavailable')
    else:
        global accountInUse
        accountInUse = len(accountDatabase)
        accountDatabase.loc[len(accountDatabase)] = [username, password, email, 0, [], [], type, []]
        saveData()
        setHomeScreen()
def showMenu():
    menuBar.delete(0, 'end')
    fileMenu = Menu(menuBar, tearoff =0)
    fileMenu.add_command(label = "Log Out", command = lambda:logOut())
    fileMenu.add_command(label = "Exit", command = lambda:startScreen.quit())
    menuBar.add_cascade(label = "Account", menu = fileMenu)
    startScreen.config(menu = menuBar)
    global accountInUse
    if accountDatabase.loc[accountInUse, 'Type'] == 'Owner':
        manageMenu = Menu(menuBar, tearoff = 0)
        manageMenu.add_command(label = "Add Business", command=addBusinessScreen)
        if isinstance(accountDatabase.loc[accountInUse, 'Businesses'],list) and accountDatabase.loc[accountInUse, 'Businesses']:
            editMenu = Menu(manageMenu, tearoff=0)
            for item in accountDatabase.loc[accountInUse, 'Businesses']:
                editMenu.add_command(label = item, command = lambda i=item:editBusiness(i))
            manageMenu.add_cascade(label = 'Edit', menu = editMenu)
        menuBar.add_cascade(label = "Manage", menu = manageMenu)
def logOut():
    createNewAccountButton.pack()
    loginButton.pack()
    usernameInput.delete(0, END)
    passwordInput.delete(0, END)
    emailInput.delete(0, END)
    usernameInput.insert(0, 'Enter Username')
    passwordInput.insert(0,'Enter Password')
    emailInput.insert(0,'Enter Email')
    usernameInput.config(fg = 'grey')
    passwordInput.config(fg = 'grey')
    emailInput.config(fg = 'grey')
    global accountInUse
    accountInUse = -1
    startScreen.config(menu = None)
def accountType():
    if usernameInput.get() == "Enter Username" or usernameInput.get() == "":
        startText.config(text = "Enter a valid username")
    elif emailInput.get() == "Enter Email" or emailInput.get() == "":
        startText.config(text = "Enter a valid email")
    elif passwordInput.get() == "Enter Password" or passwordInput.get() == "":
        startText.config(text = "Enter a valid password")
    else:
        global accountInUse
        clearScreen()
        startText.pack()
        startText.config(text = "I am a...")
        customerButton.pack()
        ownerButton.pack()
def uploadFile():
    global filePath
    filePath = filedialog.askopenfilename()
    if filePath:
        businessImageInput.config(bg = 'green')
        createBusinessText.config(text = "File Path: " + filePath)
    else:
        createBusinessText.config(text = "No file selected")
def addBusinessScreen():
    clearScreen()
    businessDescriptionInput.delete(0, END)
    businessLocationInput.delete(0, END)
    businessNameInput.delete(0, END)
    businessNameInput.insert(0, 'Business Name')
    businessLocationInput.insert(0,'Business Location')
    businessDescriptionInput.insert(0,'Business Description')
    businessDescriptionInput.config(fg = 'grey')
    businessNameInput.config(fg = 'grey')
    businessLocationInput.config(fg = 'grey')
    createBusinessTitle.pack()
    businessNameInput.pack()
    businessCategoryInput.pack()
    businessLocationInput.pack()
    businessDescriptionInput.pack()
    businessImageInput.pack()
    createBusinessButton.pack()
    createBusinessText.pack()
def addPlaceholder(entry, placeholderText):
    entry.insert(0, placeholderText)
    entry.config(fg = 'grey')
    def on_focus_in(event):
        if entry.get() == placeholderText:
            entry.delete(0, END)
            entry.config(fg = 'black')
    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholderText)
            entry.config(fg = 'grey')
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
def createBusiness(name, location, description):
    businessImageInput.config(bg = 'SystemButtonFace')
    index = businessDatabase.index[businessDatabase['Name']==name].tolist()
    global filePath
    global accountInUse
    if index:
        createBusinessText.config(text = 'Business is Already Created')
    elif businessNameInput.get()=="Business Name":
        createBusinessText.config(text = "Enter valid name")
    elif businessLocationInput.get()=="Business Location":
        createBusinessText.config(text = "Enter valid location")
    elif selectedCategory.get() == "Select Category":
        createBusinessText.config(text = "Select a category")
    elif businessDescriptionInput.get()=="Business Description":
        createBusinessText.config(text = "Enter valid description")
    elif not filePath:
        createBusinessText.config(text = "Upload Image")
    else:
        businessDatabase.loc[len(businessDatabase)] = [name, location, filePath, description, selectedCategory.get(), 0.0, 0, 0, []]
        if not isinstance(accountDatabase.at[accountInUse, 'Businesses'], list):
            accountDatabase.at[accountInUse, 'Businesses'] = []
        accountDatabase.at[accountInUse, 'Businesses'].append(name)
        saveData()
        setHomeScreen()
        filePath = ""
        createBusinessText.config(text = "")
        businessCategoryInput.set("Select Category")
def updateBusiness(updatedValue, type, index):
    if type == "Name":
        businessDatabase.loc[index, "Name"] = updatedValue
    if type == "Location":
        businessDatabase.loc[index, "Location"] = updatedValue
    if type == "Description":
        businessDatabase.loc[index, "Description"] = updatedValue
    if type == "Category":
        businessDatabase.loc[index, "Category"] = updatedValue
    if type == "Image":
        businessDatabase.loc[index, "Image"] = updatedValue
def editBusiness(item):
    clearScreen()
    global currentBusinessIndex
    indexlist = businessDatabase.index[businessDatabase['Name']==item].tolist()
    if not indexlist:
        return
    currentBusinessIndex = indexlist[0]
    editBusinessNameInput.delete(0, END)
    editBusinessNameInput.insert(0, businessDatabase.loc[currentBusinessIndex, "Name"])
    editBusinessLocationInput.delete(0, END)
    editBusinessLocationInput.insert(0, businessDatabase.loc[currentBusinessIndex, "Location"])
    editBusinessDescriptionInput.delete(0, END)
    editBusinessDescriptionInput.insert(0, businessDatabase.loc[currentBusinessIndex, "Description"])
    editSelectedCategory.insert(0, businessDatabase.loc[currentBusinessIndex, "Category"])
    editBusinessNameInput.pack()
    editBusinessLocationInput.pack()
    editBusinessCategoryInput.pack()
    editBusinessDescriptionInput.pack()
    editBusinessImageInput.pack()
    editBusinessButton.pack()
def finalizeEdits():
    global currentBusinessIndex
    global filePath
    index = currentBusinessIndex
    if editBusinessNameInput.get() != "" and editBusinessNameInput.get() != "Business Name" :
        updateBusiness(editBusinessNameInput.get(), "Name", index)
    if editBusinessLocationInput.get() != "" and editBusinessLocationInput.get() != "Business Location" :
        updateBusiness(editBusinessLocationInput.get(), "Location", index)
    if editBusinessDescriptionInput.get() != "" and editBusinessDescriptionInput.get() != "Business Description" :
        updateBusiness(editBusinessDescriptionInput.get(), "Description", index)
    if editSelectedCategory.get() != "Select Category":
        updateBusiness(editSelectedCategory.get(), "Category", index)
    if filePath:
        updateBusiness(filePath, "Image", index)
        filePath = ""
    setHomeScreen()
def clearScreen():
    for widget in startScreen.winfo_children():
        widget.pack_forget()
    titleText.pack()
def on_frame_configure(event):
    businessViewer.configure(scrollregion=businessViewer.bbox("all"))
def showBusinesses(df=None):
    imageRefs = []
    for widget in businessFrame.winfo_children():
        widget.destroy()
    if df is None:
        df = businessDatabase
    for i, row in df.iterrows():
        businessCard = Frame(businessFrame, bd =1, relief ="solid")
        businessCard.pack(padx=10,pady=5, fill = "x")
        try:
            thumbnail = Image.open(row['Image'])
            thumbnail = thumbnail.resize((80,80))
            thumbnailphoto = ImageTk.PhotoImage(thumbnail)
            thumbnailLabel = Label(businessCard, image = thumbnailphoto)
            thumbnailLabel.image = thumbnailphoto
            thumbnailLabel.pack(side="left", padx =5, pady=5)
            imageRefs.append(thumbnailphoto)
        except:
            Label(businessCard, text = "[No Image]", width =10, height =5 ).pack(side="left", padx=5, pady=5)
        businessLabel = Label(businessCard, text = row['Name'])
        businessLabel.pack(side="left", padx=10,pady=5)
        businessButton = Button(businessCard, text = "View Details", command = lambda r =row:showDetails(r))
        businessButton.pack(side="right", padx=10)
        if(row['Number of Reviews']) > 0:
            reviewLabel = Label(businessCard, text = str(round(row['Rating'], 1)) + " Stars")
            reviewLabel.pack(side = "left", padx=10)
        reviewButton = Button(businessCard, text = "Add Review", command = lambda r =row:addReviewScreen(r))
        reviewButton.pack(side="right", padx=10)
        def on_enter(e, w=businessCard):
            w.config(bg="lightblue")
        def on_leave(e, w = businessCard):
            w.config(bg="SystemButtonFace")
        businessCard.bind("<Enter>", on_enter)
        businessCard.bind("<Leave>", on_leave)
def showDetails(business):
    detailWindow = Toplevel(startScreen)
    detailWindow.title(business['Name'])
    Label(detailWindow, text= "Name: "+ business['Name']).pack(padx=10,pady=5)
    Label(detailWindow, text = "Location: "+business['Location']).pack(padx=10,pady=5)
    Label(detailWindow, text = "Category: " + business['Category']).pack(padx=10,pady=5)
    Label(detailWindow, text = "Description: " + business['Description']).pack(padx=10,pady=5)
    businessImg = Image.open((business['Image']))
    maxThumbnailWidth, maxThumbnailHeight =400,400
    businessImg.thumbnail((maxThumbnailWidth, maxThumbnailHeight))   
    businessPhoto = ImageTk.PhotoImage(businessImg)  
    businessImageLabel = Label(detailWindow, image = businessPhoto)  
    businessImageLabel.image = businessPhoto
    businessImageLabel.pack(padx=10, pady=10)
    reviewsText = "Reviews:\n"
    if isinstance(business['Reviews'], list):
        for review in business['Reviews']:
            reviewsText += review +"\n"
    reviewLabel = Label(detailWindow, text = reviewsText)
    reviewLabel.pack()
def setHomeScreen():
    clearScreen()
    showMenu()
    titleText.pack(side="top", pady=10)
    searchFrame.pack(side = "top",fill="x", padx=10, pady=5)
    searchLabel.pack(side="left", padx=(0,5))
    searchEntry.pack(side="left", fill ="x", expand = True, padx=(0,5))
    chooseCategory.pack(side = "left", padx=(5,5))
    ratingOrderInput.pack(side="left", padx=(5,5))
    goButton.pack(side="left")
    businessViewer.pack(side = "left", fill ="both", expand = True)
    viewerScrollbar.pack(side = "right", fill = "y")
    showBusinesses()
def addReviewScreen(business):
    global starButtons
    global rating
    rating.set(0)
    starButtons = []
    reviewWindow = Toplevel(startScreen)
    reviewWindow.title(business['Name'])
    Label(reviewWindow, text = "Leave a review and share your experience at " + business['Name'] + "!").pack()
    starFrame = Frame(reviewWindow)
    starFrame.pack(pady=10)
    for i in range(5):
        star = Button(starFrame, text = "☆", command = lambda i=i:setRating(i+1))
        star.pack(side="left")
        starButtons.append(star)
    reviewDescription = Text(reviewWindow, height =5, width = 40, wrap="word")
    reviewDescription.pack(fill="x")
    addTextPlaceholder(reviewDescription, "Describe Experience Here")
    submitReviewButton= Button(reviewWindow, text = "Submit Review", command = lambda:[updateReview(business, reviewDescription.get("1.0", "end-1c")), reviewWindow.destroy()] )
    submitReviewButton.pack(pady=10)
def setRating(value):
    global rating
    rating.set(value)
    updateStars()
def updateStars():
    global starButtons
    global rating
    for i in range(5):
        if i<rating.get():
            starButtons[i].config(text = "★")
        else:
            starButtons[i].config(text = "☆")
def updateReview(row, review):
    global rating
    global accountInUse
    review = review.strip()
    if review == "" or review == "Describe Experience Here":
        return
    if not isinstance(accountDatabase.loc[accountInUse, 'Reviews'], list):
        accountDatabase.loc[accountInUse, 'Reviews'] = []
    index = businessDatabase.index[businessDatabase['Name']==row['Name']].tolist()[0]
    accountDatabase.loc[accountInUse, 'Reviews'].append({"rating": rating.get(), "review":review})
    accountDatabase.loc[accountInUse, "Number of Reviews"]+= 1
    businessDatabase.loc[index, 'Number of Reviews'] +=1
    businessDatabase.loc[index, 'Total Rating Count'] += rating.get()
    if not isinstance(businessDatabase.loc[index, "Reviews"], list):
        businessDatabase.loc[index, "Reviews"] = []
    businessDatabase.loc[index, "Rating"] = businessDatabase.loc[index, 'Total Rating Count']/businessDatabase.loc[index, 'Number of Reviews']
    businessDatabase.loc[index, "Reviews"].append(f"{rating.get()}★ - {review.strip()}")
    setHomeScreen()
def addTextPlaceholder(text_widget, placeholder):
    text_widget.insert("1.0", placeholder)
    text_widget.config(fg = "grey")
    def on_focus_in(event):
        if text_widget.get("1.0", "end-1c") == placeholder:
            text_widget.delete("1.0", END)
            text_widget.config(fg = "black")
    def on_focus_out(event):
        if text_widget.get("1.0", "end-1c") == "":
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg = "grey")
    text_widget.bind("<FocusIn>", on_focus_in)
    text_widget.bind("<FocusOut>", on_focus_out)
def sortAndSearch():
    query = searchVar.get().lower()
    category = chosenCategory.get()
    rating_sort = ratingOrder.get()
    filtered = businessDatabase.copy()
    if query and query!="":
        filtered = filtered[filtered.apply(lambda row: query in row['Name'].lower() or query in row['Description'].lower(), axis=1)]
    if category != "t by Category":
        filtered = filtered[filtered['Category']==category]
    if rating_sort == "Highest to Lowest Rating":
        filtered = filtered.sort_values(by = "Rating", ascending = False)
    elif rating_sort == "Lowest to Highest Rating":
        filtered = filtered.sort_values(by = "Rating", ascending = True)
    showBusinesses(filtered)
def saveData(): 
    accountDatabase.to_csv("accounts.csv", index=False)
    businessDatabase.to_csv("businesses.csv", index = False)
startScreen = Tk()
accountInUse = -1
menuBar = Menu(startScreen)
startScreen.title("CityPulse")
startScreen.state('zoomed')
titleText = Label(startScreen, text = 'CityPulse')
titleText.pack()
filePath = ""
startText = Label(startScreen, text = '')
if os.path.exists("accounts.csv"):
    accountDatabase = pd.read_csv("accounts.csv")
    accountDatabase['Businesses'] = accountDatabase['Businesses'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else[])
    accountDatabase['Reviews'] = accountDatabase['Reviews'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
else:
    accountDatabase = pd.DataFrame(columns= ['Username', 'Password', 'Email', 'Number of Reviews', 'Certificates', 'Reviews', 'Type', 'Businesses'])
if os.path.exists("businesses.csv"):
    businessDatabase = pd.read_csv("businesses.csv")
    businessDatabase['Reviews'] = businessDatabase['Reviews'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else[])
else:
    businessDatabase = pd.DataFrame(columns = ['Name', 'Location', 'Image', 'Description', 'Category', 'Rating', 'Number of Reviews', 'Total Rating Count', 'Reviews'])
createNewAccountButton = Button(startScreen, text = 'Create New Account', command = newAccountScreen)
loginButton = Button(startScreen, text = 'Login Into Existing Account', command = loginScreen)
createNewAccountButton.pack()
loginButton.pack()
usernameInput = Entry(startScreen)
addPlaceholder(usernameInput, "Enter Username")
passwordInput = Entry(startScreen)
addPlaceholder(passwordInput, "Enter Password")
emailInput = Entry(startScreen)
addPlaceholder(emailInput, "Enter Email")
loginCompletedButton = Button(startScreen, text = 'Login', command = lambda:login(usernameInput.get(), passwordInput.get()))
createAccountCompletedButton = Button(startScreen, text = 'Create New Account', command = lambda:accountType())
customerButton = Button(startScreen, text = "Customer", command= lambda:createAccount(usernameInput.get(), passwordInput.get(), emailInput.get(), "Customer"))
ownerButton = Button(startScreen, text = "Owner", command = lambda:createAccount(usernameInput.get(), passwordInput.get(), emailInput.get(), "Owner"))
businessNameInput = Entry(startScreen)
addPlaceholder(businessNameInput, "Business Name")
businessLocationInput = Entry(startScreen)
addPlaceholder(businessLocationInput, "Business Location")
selectedCategory = StringVar()
businessCategoryInput = ttk.Combobox(startScreen, values = ['Food', 'Service', 'Retail', 'Health & Wellness', 'Education', 'Automotive', 'Travel & Hospitality', 'Entertainment', 'Home Services'], textvariable = selectedCategory, state="readonly")
businessCategoryInput.set("Select Category")
businessDescriptionInput = Entry(startScreen)
addPlaceholder(businessDescriptionInput, "Business Description")
businessImageInput = Button(startScreen, text = "Upload Business Image", command = uploadFile)
createBusinessButton = Button(startScreen, text = "Create Business", command = lambda:createBusiness(businessNameInput.get(), businessLocationInput.get(), businessDescriptionInput.get()))
createBusinessText = Label(startScreen)
createBusinessTitle = Label(startScreen,text = "Create your business!")
editBusinessNameInput = Entry(startScreen)
addPlaceholder(editBusinessNameInput, "Business Name")
editBusinessLocationInput = Entry(startScreen)
addPlaceholder(editBusinessLocationInput, "Business Location")
editSelectedCategory = StringVar()
editBusinessCategoryInput = ttk.Combobox(startScreen, values = ['Food', 'Service', 'Retail', 'Health & Wellness', 'Education', 'Automotive', 'Travel & Hospitality', 'Entertainment', 'Home Services'], textvariable = editSelectedCategory, state="readonly")
editBusinessCategoryInput.set("Select Category")
editBusinessDescriptionInput = Entry(startScreen)
addPlaceholder(editBusinessDescriptionInput, "Business Description")
editBusinessImageInput = Button(startScreen, text = "Upload Business Image", command = uploadFile)
editBusinessButton = Button(startScreen, text = "Finalize Changes", command = lambda:finalizeEdits())
editBusinessText = Label(startScreen)
homeButton = Button(startScreen, command = lambda:clearScreen())
currentBusinessIndex = -1
businessViewer = Canvas(startScreen)
viewerScrollbar = Scrollbar(startScreen, orient = "vertical", command = businessViewer.yview)
businessViewer.configure(yscrollcommand=viewerScrollbar.set)
businessFrame = Frame(businessViewer)
businessViewer.create_window((0,0), window = businessFrame, anchor = "nw")
businessFrame.bind("<Configure>", on_frame_configure)
rating = IntVar(value = 0)
starButtons = []
searchFrame = Frame(startScreen)
searchLabel = Label(searchFrame, text = "Search:")
searchVar = StringVar()
searchEntry = Entry(searchFrame, textvariable = searchVar)
searchEntry.bind("<Return>", lambda e: sortAndSearch())
chosenCategory = StringVar()
chooseCategory = ttk.Combobox(searchFrame, values = ['Food', 'Service', 'Retail', 'Health & Wellness', 'Education', 'Automotive', 'Travel & Hospitality', 'Entertainment', 'Home Services'], textvariable = chosenCategory, state = "readonly")
chooseCategory.set("Sort by Category")
ratingOrder = StringVar()
ratingOrderInput = ttk.Combobox(searchFrame, values = ['Highest to Lowest Rating', 'Lowest to Highest Rating'], textvariable= ratingOrder, state = 'readonly')
ratingOrderInput.set("Sort by Rating")
goButton = Button(searchFrame, text = "Sort and Search", command = lambda:sortAndSearch())
startScreen.mainloop()