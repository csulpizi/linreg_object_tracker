## LinReg Object Tracker
A motion tracker that uses linear regression to predict the trajectory  of items on screen to determine which items belong to which objects.

### track_objects() Function
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

### track_plot() Function
A function used by track_objects to plot the results. 

### Required Libraries
* numpy
* matplotlib

### Selecting an m Value
The higher the m-value the more linear the predicted trajectory becomes. If the value is too high then the function would fail to detect any changes in direction or speed.

The lower the m-value the more labile the predicted trajectory becomes. If the m-value is 2, for example, then the trajectory would simply be the line that the last two points went through. The trajectory would therefore become easily influenced by noise.

A good m value is therefore a value that is small enough to detect changes in trajectory without being too small. The ideal m value largely depends on the frame rate of your data. It is recommended that you use the default value, then use the verbose plotting function to decide whether or not the value should be increased or decreased. 

### Selecting a bound_tight Value
This value depends on how much noise exists in your data set. If the noise is nearly non-existant, then the bound could be very low with no issue. If there is a lot of noise, then you may need a larger bound to make sure the algorithm correctly identifies points in each object. 

If the bound_tight is too small, then the predicted trajectories may be over-segmented (when the true trajectory of an object is incorrectly identified as multiple objects), or fail to see the objects at all.

If the bound_tight is too large, then the algorithm may incorrectly assign items to the wrong objects (under-segmentation).

Again, it is recommended that you use the default, then use the verbose plot function to decide whether or not the value needs to be changed. 

### Selecting a time_limit Value


### Limitations

