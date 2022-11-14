# ISMR_processing
##### 1. Copy_ISMRs.ipynb 
This notebook is to segrigate daily .ismr files from the raw .sbf files.

##### 2. ISMR_processing_final.ipynb
This nodebook is to process daily (one day) .ismr files. It concatenate hourly files into one. 
Nomenculture of concatenated file would be as following-
  
        
        concated_%y%d.ismr ===>   
                            
                            %y = last two digit of year, Ex. year 2022 then %y =22
                            %d = day of year in three digits, Ex. 5 January then %d = 005
                            
                           Ex. concated_22001.ismr is concetinated file for 1 January 2022.
                           
                           
                        


##### 3. ismr_processing_period.ipynb
This ipython notebook is to process the data for the required duration and provide average values of TEC for all selected days.
