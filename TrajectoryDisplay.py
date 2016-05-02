from Tkinter import *
from tkFileDialog import askopenfilename
from PIL import Image, ImageTk
from Structs.Segment import Segment
import cv2
import csv


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class Application(Frame):
    def __init__(self, master=None):
        self.root = master
        Frame.__init__(self, master)
        # width x height + x_offset + y_offset:
        self.root.geometry("175x400+30+30")
        self.opencv_image = None
        self.opencv_image_marked = None
        self.imageWidth = 0
        self.imageLength = 0
        self.trajectoryFilename = ""
        self.startX = 0
        self.startY = 0
        self.createWidgets()

    def createWidgets(self):

        self.widthLabel = Label(self.root, text="Course Width (in):")
        self.widthLabel.grid(row=0, column=1)
        self.widthEntry = Entry(self.root)
        self.widthEntry.grid(row=1, column=1)

        self.lengthLabel = Label(self.root, text="Course Length (in):")
        self.lengthLabel.grid(row=2, column=1)
        self.lengthEntry = Entry(self.root)
        self.lengthEntry.grid(row=3, column=1)

        self.openImage = Button(self.root, text="Open Image File", command=self.openImage)
        self.openImage.grid(row=4, column=1)
        self.openImageLabel = Label(self.root, text="")
        self.openImageLabel.grid(row=5, column=1)
        self.clearImage = Button(self.root, text="Clear Image", command=self.clearImage)
        self.clearImage.grid(row=6, column=1)

        Label(self.root, text="Drivetrain Type").grid(row=8, column=1)
        self.drivetrainOption = StringVar(self.root)
        self.drivetrainOption.set("Tank")
        self.drivetrainOption.trace("w", self.switchDrivetrainType)
        self.drivetrainEntry = OptionMenu(self.root, self.drivetrainOption, "Tank", "Swerve")
        self.drivetrainEntry.grid(row=9, column=1)

        self.openTrajectory = Button(self.root, text="Select Trajectory File", command=self.openTrajectory)
        self.openTrajectory.grid(row=11, column=1)
        self.openTrajectoryLabel = Label(self.root, text="")
        self.openTrajectoryLabel.grid(row=12, column=1)
        self.clearTrajectoryButton = Button(self.root, text="Clear Trajectory", command=self.clearTrajectory)
        self.clearTrajectoryButton.grid(row=13, column=1)

        self.originalTrajectoryCheckboxValue = IntVar()
        self.originalTrajectoryCheckboxValue.set(1)
        self.originalTrajectoryCheckboxValue.trace("w", self.drawTrajectory)
        self.originalTrajectoryCheckbox = Checkbutton(self.root, text="Original Trajectory", variable=self.originalTrajectoryCheckboxValue)
        self.originalTrajectoryCheckbox.grid(row=14, column=1)

        self.leftTrajectoryCheckboxValue = IntVar()
        self.leftTrajectoryCheckboxValue.set(1)
        self.leftTrajectoryCheckboxValue.trace("w", self.drawTrajectory)
        self.leftTrajectoryCheckbox = Checkbutton(self.root, text="Left Trajectory", variable=self.leftTrajectoryCheckboxValue)
        self.leftTrajectoryCheckbox.grid(row=15, column=1)

        self.rightTrajectoryCheckboxValue = IntVar()
        self.rightTrajectoryCheckboxValue.set(1)
        self.rightTrajectoryCheckboxValue.trace("w", self.drawTrajectory)
        self.rightTrajectoryCheckbox = Checkbutton(self.root, text="Right Trajectory", variable=self.rightTrajectoryCheckboxValue)
        self.rightTrajectoryCheckbox.grid(row=16, column=1)

        self.frontLeftTrajectoryCheckboxValue = IntVar()
        self.frontLeftTrajectoryCheckboxValue.set(1)
        self.frontLeftTrajectoryCheckboxValue.trace("w", self.drawTrajectory)
        self.frontLeftTrajectoryCheckbox = Checkbutton(self.root, text="Front Left Trajectory", variable=self.frontLeftTrajectoryCheckboxValue)

        self.frontRightTrajectoryCheckboxValue = IntVar()
        self.frontRightTrajectoryCheckboxValue.set(1)
        self.frontLeftTrajectoryCheckboxValue.trace("w", self.drawTrajectory)
        self.frontRightTrajectoryCheckbox = Checkbutton(self.root, text="Front Right Trajectory", variable=self.frontRightTrajectoryCheckboxValue)

        self.backLeftTrajectoryCheckboxValue = IntVar()
        self.backLeftTrajectoryCheckboxValue.set(1)
        self.backLeftTrajectoryCheckboxValue.trace("w", self.drawTrajectory)
        self.backLeftTrajectoryCheckbox = Checkbutton(self.root, text="Back Left Trajectory", variable=self.backLeftTrajectoryCheckboxValue)

        self.backRightTrajectoryCheckboxValue = IntVar()
        self.backRightTrajectoryCheckboxValue.set(1)
        self.backRightTrajectoryCheckboxValue.trace("w", self.drawTrajectory)
        self.backRightTrajectoryCheckbox = Checkbutton(self.root, text="Back Right Trajectory", variable=self.backRightTrajectoryCheckboxValue)

        #Button(self.root, text="Draw Trajectories", command=self.drawTrajectory).grid(row=15, column=1)

        self.warningLabel = Label(self.root, fg="yellow", text="")
        self.warningLabel.grid(row=17, column=1)
        self.errorLabel = Label(self.root, fg="red", text="")
        self.errorLabel.grid(row=18, column=1)

    def openImage(self):
        options = {'filetypes': [('JPEG', '.jpg'), ('PNG', '.png')], 'initialdir': '.', 'parent': self.root}

        imageFilename = askopenfilename(**options)
        if(imageFilename != ""):
            dot = imageFilename.find(".")
            extension = imageFilename[dot:]
            if extension in ['.jpg', '.jpeg', '.png', '.tiff']:
                self.opencv_image = cv2.imread(imageFilename)
                cv2.putText(self.opencv_image, "X", (20, 15), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255))
                cv2.line(self.opencv_image, (20, 20), (30, 20),  (0, 0, 255), 2)
                cv2.putText(self.opencv_image, "Y", (5, 30), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 0, 0))
                cv2.line(self.opencv_image, (20, 20), (20, 30),  (255, 0, 0), 2)
                self.opencv_image_marked = self.opencv_image.copy()
                self.setImage()
                self.openImageLabel['text'] = imageFilename.rsplit('/', 1)[-1]

    def setImage(self):
        image = Image.fromarray(cv2.cvtColor(self.opencv_image_marked, cv2.COLOR_BGR2RGB))
        photoimage = ImageTk.PhotoImage(image)
        self.image = Label(self.root, image=photoimage)
        self.image.image = photoimage
        self.image.grid(row=0, column=0, rowspan=25)
        self.image.bind('<Button-1>', self.mouse_click)
        (self.imageWidth, self.imageLength) = image.size
        self.root.geometry("%dx%d+30+30" % (self.imageWidth + 175, self.imageLength))

    def mouse_click(self, event):
        self.startX = event.x
        self.startY = event.y
        if hasattr(self, 'trajectory') and not self.trajectory is None:
            self.drawTrajectory()
        else:
           self.opencv_image_marked = self.opencv_image.copy() 
        cv2.circle(self.opencv_image_marked, (event.x, event.y), 3, (0, 255, 0), 2)
        self.setImage()

    def clearImage(self):
        self.openLabel['text'] = ""
        self.image.destroy()
        self.root.geometry("175x400+30+30")

    def loadTrajectory(self, file, trajectory):
        reader = csv.DictReader(file)
        for row in reader:
            trajectory.append(Segment(float(row['dt']), float(row['x']), float(row['y']), float(row['position']), float(row['velocity']), float(row['acceleration']), float(row['jerk']), float(row['heading'])))

    def openTrajectory(self):
        options = {'filetypes': [('CSV', '.csv')], 'initialdir': '.', 'parent': self.root}

        trajectoryFilename = self.trajectoryFilename = askopenfilename(**options)
        self.openTrajectoryLabel['text'] = trajectoryFilename.rsplit('/', 1)[-1]
        trajectoryFile = open(trajectoryFilename, "r")
        self.trajectory = []
        self.loadTrajectory(trajectoryFile, self.trajectory)

        drivetrain = self.drivetrainOption.get()
        if(drivetrain == 'Tank'):
            self.openTankTrajectory(trajectoryFilename)
        elif(drivetrain == 'Swerve'):
            self.openSwerveTrajectory(trajectoryFilename)

        self.drawTrajectory()

    def openTankTrajectory(self, filename):
        '''
        if filename == "":
            return
        leftTrajectoryFilename = filename.substr('/', 1)[:-1] + "left_" + filename.rsplit('/', 1)[-1]
        leftTrajectoryFile = open(leftTrajectoryFilename, "r")
        self.leftTrajectory = []
        self.loadTrajectory(leftTrajectoryFile, self.leftTrajectory)

        rightTrajectoryFilename = "right_" + trajectoryFilename
        rightTrajectoryFile = open(rightTrajectoryFilename, "r")
        self.rightTrajectory = []
        self.loadTrajectory(rightTrajectoryFile, self.rightTrajectory)
        '''
        return

    def openSwerveTrajectory(self, filename):
        if filename == "":
            return
        frontLeftTrajectoryFilename = "front_left_" + trajectoryFilename
        frontLeftTrajectoryFile = open(frontLeftTrajectoryFilename, "r")
        self.frontLeftTrajectory = []
        self.loadTrajectory(frontLeftTrajectoryFile, self.frontLeftTrajectory)

        frontRightTrajectoryFilename = "front_right_" + trajectoryFilename
        frontRightTrajectoryFile = open(frontRightTrajectoryFilename, "r")
        self.frontRightTrajectory = []
        self.loadTrajectory(frontRightTrajectoryFile, self.frontRightTrajectory)

        backLeftTrajectoryFilename = "back_left_" + trajectoryFilename
        backLeftTrajectoryFile = open(backLeftTrajectoryFilename, "r")
        self.backLeftTrajectory = []
        self.loadTrajectory(backLeftTrajectoryFile, self.backLeftTrajectory)

        backRightTrajectoryFilename = "back_right_" + trajectoryFilename
        backRightTrajectoryFile = open(backRightTrajectoryFilename, "r")
        self.backRightTrajectory = []
        self.loadTrajectory(backRightTrajectoryFile, self.backRightTrajectory)

    def clearTrajectory(self):
        self.trajectoryFilename = ""
        self.trajectory = None
        self.leftTrajectory = None
        self.rightTrajectory = None
        self.frontLeftTrajectory = None
        self.frontRightTrajectory = None
        self.backLeftTrajectory = None
        self.backRightTrajectory = None
        if(self.opencv_image is not None):
            self.opencv_image_marked = self.opencv_image.copy()
            self.setImage()

    def switchDrivetrainType(self):
        drivetrain = self.drivetrainOption.get()
        if drivetrain == 'Tank':
            self.leftTrajectoryCheckbox.grid(row=15, column=1)
            self.rightTrajectoryCheckbox.grid(row=16, column=1)
            self.frontLeftTrajectoryCheckbox.grid_forget()
            self.frontRightTrajectoryCheckbox.grid_forget()
            self.backLeftTrajectoryCheckbox.grid_forget()
            self.backRightTrajectoryCheckbox.grid_forget()
            self.openTankTrajectory(self.trajectoryFilename)
        elif drivetrain == 'Swerve':
            self.leftTrajectoryCheckbox.grid_forget()
            self.rightTrajectoryCheckbox.grid_forget()
            self.frontLeftTrajectoryCheckbox.grid(row=15, column=1)
            self.frontRightTrajectoryCheckbox.grid(row=16, column=1)
            self.backLeftTrajectoryCheckbox.grid(row=17, column=1)
            self.backRightTrajectoryCheckbox.grid(row=18, column=1)
            self.openSwerveTrajectory(self.trajectoryFilename)

    def drawTrajectory(self, *args):
        courseWidth = self.widthEntry.get()
        courseLength = self.lengthEntry.get()
        if not is_number(courseWidth) and not is_number(courseLength):
            self.errorLabel['text'] = "Course Width is not set\nCourse Length is not set"
            self.widthEntry['bg'] = "red"
            self.lengthEntry['bg'] = "red"
            return
        elif not is_number(courseWidth):
            self.errorLabel['text'] = "Course Width is not set"
            self.widthEntry['bg'] = "red"
            self.lengthEntry['bg'] = "white"
            return
        elif not is_number(courseLength):
            self.errorLabel['text'] = "Course Length is not set"
            self.lengthEntry['bg'] = "red"
            self.widthEntry['bg'] = "white"
            return
        else:
            self.errorLabel['text'] = ""
            self.lengthEntry['bg'] = "white"
            self.widthEntry['bg'] = "white"

        self.opencv_image_marked = self.opencv_image.copy()
        if self.originalTrajectoryCheckboxValue.get() == 1:
            for i in range(len(self.trajectory) - 1):
                curr_seg = self.trajectory[i]
                next_seg = self.trajectory[i + 1]

                p1 = (int(self.imageWidth * curr_seg.x / float(courseWidth)) + self.startX, int(self.imageLength * curr_seg.y / float(courseLength)) + self.startY)
                p2 = (int(self.imageWidth * next_seg.x / float(courseWidth)) + self.startX, int(self.imageLength * next_seg.y / float(courseLength)) + self.startY)

                cv2.line(self.opencv_image_marked, p1, p2, (0, 0, 255), 2)

                self.setImage()


root = Tk()
root.title("Trajectory Display")
app = Application(master=root)
app.mainloop()
root.destroy()
