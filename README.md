## LinReg Object Tracker
A motion tracker that uses linear regression to predict the trajectory  of items on screen to determine which items belong to which objects.

###track_objects() Function
Uses linear regression to predict the trajectory of items on screen to determine which items belong to which objects.

Required Inputs:
**IMPORTANT**: Make sure that the x and y values are scaled such that they are between 0 and 1. 
* x -> Shape (n, ). The x coordinates of each of n objects. 
* y -> Shape (n, ). The y coordinates of each of n objects. 
* t -> Shape (n, ). The time stamps of each of n objects. 

Optional Inputs: 
* m -> The number of most recent items in each object used to calculate the polynomial's parameters. 
* bound_tight -> The maximum euclidean distance an item can be from an object's predicted location to be considered a member of that object.
* time_limit -> The amount of time that can pass before an object is considered "inactive". Once that many time stamps are exceeded from an object's most recent item, that object is considered finished.
* vb -> A list of t values. The program will plot all of the active objects and items on screen for each of the t values provided.
* vb_save -> A string containing a file path. If vb_save is set, the program will save all of the plots from the timestamps defined in vb to the file path specified. For example, if vb_save = "C:\image" and vb = [1,3], then two files C:\image_00001.png and C:\image_00003.png will be saved. Use backslashes rather than slashes for the file path

Outputs:
* obj_list -> A list of objects. Each entry contains a list of the indices of all items belonging to that object.
