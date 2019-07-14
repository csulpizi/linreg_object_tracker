#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linear Regressor Object Tracking
------------------------------------------------------------------------------
v1.0 - 2018-07-25 - Original. Algorithm: robust estimation.
v1.1 - 2019-05-27 - Improved readability.
v2.0 - 2019-06-24 - Changed algorithm: frame by frame association. The previous 
    algorithm was not good enough at detecting changes in trajectory, since it 
    was trying to fit each object's motion to a single curve rather than a series
    of curves. 
v2.1 - 2019-07-12 - Improved readability.
v2.2 - 2019-07-14 - Added plotting functionality
------------------------------------------------------------------------------

The track_objects function uses linear regression to predict the trajectory 
of items on screen to determine which items belong to which objects.

Each object's trajectory is plotted using the following linear functions:
    x(t) = β_x0 + β_x1 t
    y(t) = β_y0 + β_y1 t

"Item" -> A single data point
"Object" -> A series of data points is assumed to belong to the same object 
        moving through space
"""

import numpy as np
import matplotlib.pyplot as plt

def track_objects(x, y, t, m=5, bound_tight = 0.05, time_limit = 5, vb=[], vb_save=""):
    """ 
    Uses linear regression to predict the trajectory 
    of items on screen to determine which items belong to which objects.
    
    Required Inputs:
        x -> Shape (n, ). The x coordinates of each of n objects. 
        y -> Shape (n, ). The y coordinates of each of n objects. 
        **IMPORTANT**: Make sure that the x and y values are scaled such that
                they are between 0 and 1. 
        t -> Shape (n, ). The time stamps of each of n objects. 
        
    Optional Inputs: t is 
                recommended that you use a larger m values.
        m -> The number of most recent items in each object used to calculate
                the polynomial's parameters. 
        bound_tight -> The maximum euclidean distance an item can be from an object's
                predicted location to be considered a member of that object.
        time_limit -> The amount of time that can pass before an object is considered
                "inactive". Once that many time stamps are exceeded from an object's
                most recent item, that object is considered finished.
        vb -> A list of t values. The program will plot all of the active objects 
                and items on screen for each of the t values provided.
        vb_save -> A string containing a file path. If vb_save is set, the program
                will save all of the plots from the timestamps defined in vb to
                the file path specified. For example, if vb_save = "C:\image" and
                vb = [1,3], then two files C:\image_00001.png and C:\image_00003.png will be
                saved. Use backslashes rather than slashes for the file path
                
    Outputs:
        obj_list -> A list of objects. Each entry contains a list of the indices of
                all items belonging to that object.
    """
    
    ## Ensure all arrays inputted are the right data types
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    t = np.asarray(t, dtype=np.int32)
    m = int(m)
    
    ## Validate inputs
    if np.max(x) > 1.0: raise Exception("x values must not be greater than 1.0, whereas the x array inputted has an entry with value "+str(np.max(x)))
    if np.max(y) > 1.0: raise Exception("y values must not be greater than 1.0, whereas the y array inputted has an entry with value "+str(np.max(y)))
    if np.min(x) < 0.0: raise Exception("x values must not be less than 0.0, whereas the x array inputted has an entry with value "+str(np.min(x)))
    if np.min(y) < 0.0: raise Exception("y values must not be less than 0.0, whereas the y array inputted has an entry with value "+str(np.min(y)))
    if len(x.shape) > 1: raise Exception("x should be an array with shape(n, ), whereas the x array inputted has more than one dimension.")
    if x.shape != y.shape: raise Exception("The shapes of x and y must be equal, whereas the shapes of x and y are "+str(x.shape)+" and "+str(y.shape)+" respectively.")
    if x.shape != t.shape: raise Exception("The shapes of x and t must be equal, whereas the shapes of x and t are "+str(x.shape)+" and "+str(t.shape)+" respectively.")
    if m < 1: raise Exception("m must be at least 1, whereas m was "+str(m))
    
    ## items_per t is a list with an entry for each time-stamp. Each entry is a 
    ## list that contains all items in that time stamp. Add 5 "extra" lists to the 
    ## list to avoid a "list index out of range" error since the algorithm looks 
    ## 5 steps into the future
    items_per_t = [[] for c_t in range(np.max(t)+6)]
    for c_i, c_t in enumerate(t): items_per_t[c_t].append(c_i)
    
    ## obj_list is a list containing all of the objects. Each entry is a list of
    ## all of the items belonging to that object. 
    obj_list = [] ## All of the objects themselves
    
    s_act_obj = []  ## Indices (related to obj_list) of all "active" objects. Shape (?,)
    s_act_par_x = np.zeros((0,2)) ## x parameters of each of the active objects. Shape (? , 2)
    s_act_par_y = np.zeros((0,2))
    
    ## s_cur_items contains all items in the current frame. Shape (?, )
    s_cur_items = items_per_t[0]
    
    ## Set up colormap and circle coordinates for plotting
    if len(vb)>0: 
        plt.rcParams.update({'figure.max_open_warning': 0})    

    ## For each time step in the data
    for c_t in range(1, np.max(t)+1):
        
        ## If there is at least one active object
        if(len(s_act_obj) > 0):
            
            ## true_ind is an array of all of the active object indices whose last time stamp
            ## is not more than time_limit away from the current frame
            ## On the other hand, if the object's most recent time stamp is too
            ## old, its index is not included in true_ind
            true_ind = np.asarray([t[obj_list[c_i][-1]] > c_t - time_limit for c_i in s_act_obj])
            
            ## Remove all objects from s_act_obj whose most recent time_stamp
            ## is too old
            s_act_obj = np.take(s_act_obj, np.where(true_ind)[0])
            s_act_obj = s_act_obj.tolist()
            
            ## Remove those objects from the parameter sets too
            s_act_par_x = np.take(s_act_par_x, np.where(true_ind)[0], axis=0)
            s_act_par_y = np.take(s_act_par_y, np.where(true_ind)[0], axis=0)
    
        ## s_past_items is all of the the items in the previous time step
        s_past_items = s_cur_items
        
        s_cur_items = items_per_t[c_t] ## Update s_cur_items
        
        if c_t in vb:  ## If this time stamp is in vb, plot the results for this frame
            track_plot(c_t, s_act_obj, s_cur_items, s_past_items, obj_list, x, y, t, m, s_act_par_x, s_act_par_y, vb_save, bound_tight)
        
        ## If there is at least one active object and there is at least one item in this frame
        if(len(s_act_obj) > 0 and len(s_cur_items) > 0):
        
            ## s_temp_obj is a temporary copy of s_act_obj. This allows us to
            ## temporarily manipulate the set without manipulating s_act_obj
            s_temp_obj = s_act_obj[:]
            
            ## calculate the predicted location of the next item in each active object
            s_temp_x = np.expand_dims(np.sum(s_act_par_x * [1, c_t],1),-1)
            s_temp_y = np.expand_dims(np.sum(s_act_par_y * [1, c_t],1),-1)
            
            ## find the x and y positions of all items in s_cur_items
            s_cur_x = np.expand_dims(np.take(x, s_cur_items),axis=0)
            s_cur_y = np.expand_dims(np.take(y, s_cur_items),axis=0)
            
            ## calculate the distance between each item in s_cur_item and each active obj's predicted location
            dist = np.sqrt((s_temp_x - s_cur_x)**2 + (s_temp_y - s_cur_y)**2)
            
            ## Keep looping so long as there are still items in s_temp_obj and s_cur_items
            while(len(s_temp_obj) > 0 and len(s_cur_items) > 0):    
                
                ## find the index of the minimum value in dist
                min_ind = np.unravel_index(np.argmin(dist), dist.shape)
                
                ## if the distance at the minimum index is less than the tight bound
                if dist[min_ind] < bound_tight:
                    
                    ## find the indices of the object and the item with the minimum distance
                    ## (note that the index of an item in s_cur_items is not the same as the
                    ## actual index of that item in the provided date, and same for s_temp_obj 
                    ## and the actual index of that object in obj_list)
                    ind_obj = s_temp_obj[min_ind[0]]
                    ind_item = s_cur_items[min_ind[1]]
                    
                    ## Add that item to the appropriate obj_list entry
                    obj_list[ind_obj].append(ind_item)
                    
                    ## Remove obj from s_temp_obj, and delete its associated row in dist
                    temp_ind = list(range(len(s_temp_obj)))
                    del temp_ind[min_ind[0]]
                    del s_temp_obj[min_ind[0]]
                    dist = dist[temp_ind, :]    
                    
                    ## Remove item from s_cur_items, and delete its associated column in dist
                    temp_ind = list(range(len(s_cur_items)))
                    del temp_ind[min_ind[1]]
                    del s_cur_items[min_ind[1]]
                    dist = dist[:, temp_ind] 
                    
                    ## Find the t, x, and y values of the m most recent items belonging
                    ## to that object
                    temp_t = np.take(t, obj_list[ind_obj][-m:])
                    temp_x = np.take(x, obj_list[ind_obj][-m:])
                    temp_y = np.take(y, obj_list[ind_obj][-m:])
                    
                    ## Find the index of the object in s_act_obj
                    temp_ind = np.argmax(s_act_obj == np.expand_dims(ind_obj,0))
                    
                    ## Set up and solve the linear equation to find the new x parameters
                    ## for that object using the m most recent items
                    A = np.asarray([[len(temp_t), np.sum(temp_t)],[np.sum(temp_t), np.sum(temp_t.astype(np.int64) ** 2)]])
                    B = np.asarray([[np.sum(temp_x)], [np.sum(temp_x * temp_t)]])  
                    s_act_par_x[temp_ind,:] = np.transpose(np.linalg.solve(A,B))
                    
                    ## Do the same for y
                    B = np.asarray([[np.sum(temp_y)], [np.sum(temp_y * temp_t)]])  
                    s_act_par_y[temp_ind,:] = np.transpose(np.linalg.solve(A,B))
                    
                ## Stop looping if the minimum distance exceeds the tight bound
                else: break    
    
            ## true_ind is an array with the indices of all active objects
            ## whose predicted locations in this time stamp do not exceed the bounds
            ## of the stage. For example, an object whose predicted location is 
            ## x > 1 + bound_tight exceeds the right-most bound of the stage, and 
            ## is therefore not included in true_ind
            true_ind = (s_temp_x > - bound_tight) * (s_temp_x < 1 + bound_tight) * (s_temp_y > - bound_tight) * (s_temp_y < 1 + bound_tight)
        
            ## Remove all objects whose predicted locations exceed the bounds of
            ## the stage from the set of active objects
            s_act_obj = np.take(s_act_obj, np.where(true_ind[:,0])[0])
            s_act_obj = s_act_obj.tolist()
            
            ## Remove those objects from the parameter sets too
            s_act_par_x = np.take(s_act_par_x, np.where(true_ind[:,0])[0], axis=0)
            s_act_par_y = np.take(s_act_par_y, np.where(true_ind[:,0])[0], axis=0)
            
        ## If there are items "left over" in the past frame and the current frame
        if(len(s_cur_items) > 0 and len(s_past_items) > 0): 
            
            ## Find all the items in the next 5 frames
            s_temp_items = items_per_t[c_t + 1] + items_per_t[c_t + 2] + items_per_t[c_t + 3] + items_per_t[c_t + 4] + items_per_t[c_t + 5]
            
            ## Find those items' t, x, and y values
            temp_t = np.take(t, s_temp_items)
            temp_x = np.take(x, s_temp_items)
            temp_y = np.take(y, s_temp_items)
            
            ## Keep looping so long as there are items "left over" in the past frame and the current frame
            while(len(s_cur_items) > 0 and len(s_past_items) > 0): 
            
                temp_pair = []
                temp_param_x = []
                temp_param_y = []
                temp_score_tight = []
                temp_score_loose = []
                
                ## Try each combination of items from s_past_items and s_cur_items
                for c_item_0 in s_past_items:
                    for c_item_1 in s_cur_items:
                        
                        ## Find the x slope and intercept that defines the line that intersects these two points
                        temp_slope = (x[c_item_1] - x[c_item_0])
                        temp_intercept = x[c_item_0] - t[c_item_0] * temp_slope
                        temp_param_x.append([temp_intercept, temp_slope])

                        ## Find the y slope and intercept
                        temp_slope = (y[c_item_1] - y[c_item_0])
                        temp_intercept = y[c_item_0] - t[c_item_0] * temp_slope
                        temp_param_y.append([temp_intercept, temp_slope])
                        
                        ## Using those parameters, calculate the predicted locations
                        ## of the next 5 points
                        temp_x_pos = temp_param_x[-1][0] + temp_param_x[-1][1] * (temp_t)
                        temp_y_pos = temp_param_y[-1][0] + temp_param_y[-1][1] * (temp_t)
                        
                        ## Calculate the distance between the predicted positions and the
                        ## actual positions
                        temp_dist = np.sqrt((temp_x_pos - temp_x)**2 + (temp_y_pos - temp_y)**2)
                        
                        ## Record the pairing
                        temp_pair.append([c_item_0, c_item_1])
                        
                        ## Record the "scores" for this pairing. The tight score
                        ## are the number of dist values that are smaller than the
                        ## tight bound, and the loose score is the number of dist
                        ## values that are smaller than a looser bound
                        temp_score_tight.append(np.sum(temp_dist < bound_tight))
                        temp_score_loose.append(np.sum(temp_dist < bound_tight * 2))
                        
                ## So long as one of the pairings have at least one point within 
                ## the tight bound
                if(np.max(temp_score_tight) > 1):
                    
                    ## Find the pairing with the maximum overall score
                    temp_ind = np.argmax(np.asarray(temp_score_tight) + np.asarray(temp_score_loose))
                    
                    ## Create a new object that contains those two items
                    obj_list.append(temp_pair[temp_ind])
                    
                    ## Add that item and its parameters to the active list
                    s_act_obj.append(len(obj_list) - 1)
                    s_act_par_x = np.vstack((s_act_par_x,np.asarray(temp_param_x[temp_ind])))
                    s_act_par_y = np.vstack((s_act_par_y,np.asarray(temp_param_y[temp_ind])))
                    
                    ## Remove those items from the s_past_items and s_cur_items
                    s_past_items.remove(temp_pair[temp_ind][0])
                    s_cur_items.remove(temp_pair[temp_ind][1])
                    
                ## When none of the pairings have a tight bound score > 1, break
                else: break
    
    return obj_list

def track_plot(c_t, s_act_obj, s_cur_items, s_past_items, obj_list, x, y, t, m, s_act_par_x, s_act_par_y, vb_save, bound_tight):
    """
    Plotting function for the track_objects function
    """
    
    ## Colour map
    cmap = ['#440154','#4889ca','#32ce13','#fdc825','#fd2525','#00fff0']
            
    ## Points on the circle for the bound_tight visualization
    circle_x = np.asarray([np.cos(c_rad) for c_rad in np.arange(0, np.pi*2+1e-5, np.pi*2 / 36)]) * bound_tight
    circle_y = np.asarray([np.sin(c_rad) for c_rad in np.arange(0, np.pi*2+1e-5, np.pi*2 / 36)]) * bound_tight

    ## Set up plot and title    
    plt.figure(figsize=(6,6), dpi=80)
    plt.title("t = "+str(c_t))
    
    ## Plot all of the past points in all of the active objects
    plot_x = []
    plot_y = []
    plot_c = []
    for c_obj in s_act_obj:
        for c_item in obj_list[c_obj]:
            plot_x.append(x[c_item])
            plot_y.append(y[c_item])
            plot_c.append(cmap[c_obj % 6])
    plt.scatter(plot_x,plot_y,c=plot_c, marker='x')
    
    ## Plot all of the points that were "left over" from the previous frame (ie, not in an active object)
    plot_x = [x[c_item] for c_item in s_past_items]
    plot_y = [y[c_item] for c_item in s_past_items]    
    plt.scatter(plot_x,plot_y,c="#cccccc", marker='x')
    
    ## Plot all of the items in the current frame
    plot_x = [x[c_item] for c_item in s_cur_items]
    plot_y = [y[c_item] for c_item in s_cur_items]
    plt.scatter(plot_x,plot_y,c="#222222", marker='x')
                
    ## For each object, plot the line of motion and the bound_tight circle
    for c_i, c_obj in enumerate(s_act_obj):
        m_adj = np.minimum(len(obj_list[c_obj]),m)
        plot_x = [np.sum(s_act_par_x[c_i] * [1, t[obj_list[c_obj][-m_adj]]]), np.sum(s_act_par_x[c_i] * [1,c_t])]
        plot_y = [np.sum(s_act_par_y[c_i] * [1, t[obj_list[c_obj][-m_adj]]]), np.sum(s_act_par_y[c_i] * [1,c_t])]
        plt.plot(plot_x,plot_y,c=cmap[c_obj % 6])
        plt.plot(circle_x + plot_x[-1], circle_y + plot_y[-1], c="#cccccc")
    
    ## Set the limits for the plot and either show or save it
    plt.xlim(0.0,1.0)
    plt.ylim(0.0,1.0)
    if len(vb_save) > 0: plt.savefig(vb_save + "_" + str(int(c_t + 1e5))[-5:])
    else: plt.show()