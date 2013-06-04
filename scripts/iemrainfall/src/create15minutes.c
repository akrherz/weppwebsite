/***********************************************************************
  
  	program create15minutes.c
   
  Who knows what this program does - please write me...
  
  USAGE:  ./create15minutes.exe list.txt 3
  
  INPUT:  1) filelist of reflectivity files (each file is 464 by 464)
  		  2) number of files in filelist 
  		  
  OUTPUT: file that in 15-minutes rain accumulation
  
  Algorithm of converting levels of reflectivity into reflectivity:
    
  Level      Range of reflectivity    Reflectivity 
  ------------------------------------------------------  
      0           0 <= dbZ <  5            0 dbZ
      1           5 <= dbZ < 10            0 dbZ
      2          10 <= dbZ < 15           10 dbZ
      3          15 <= dbZ < 20           15 dbZ
      4          20 <= dbZ < 25           20 dbZ
      5          25 <= dbZ < 30           25 dbZ
      6          30 <= dbZ < 35           30 dbZ
      7          35 <= dbZ < 40           35 dbZ
      8          40 <= dbZ < 45           40 dbZ
      9          45 <= dbZ < 50           45 dbZ
     10          50 <= dbZ < 55           50 dbZ
     11          55 <= dbZ < 60           55 dbZ
     12          60 <= dbZ < 65            0 dbZ
     13          65 <= dbZ < 70            0 dbZ
     14          70 <= dbZ < 75            0 dbZ
     15          75 <= dbZ                 0 dbZ
     
     
  
                     michal-kraszewski@uiowa.edu          
 26 May 2004 Fix a bug in conversion, I think?  Daryl
 ***********************************************************************/

#include<stdio.h>
#include<math.h>
#define NUM 215296 		/*Number of values in files */
#define NUMc 464   		/*Number of columns in files */
#define NUMr 464   		/*Number of rows in files */

float array[NUM]={0.0}; 
float addRarray[NUM]={0.0};
float Ravearray[NUM]={0.0};
float Rarray[NUM]={0.0};
float Zarray[NUM]={0.0};


main(int argc, char *argv[])
{
  

  int j, i; 
  int m, n; 
  int z;
  char num[1];
  char filename1[50];
  FILE *fplistfiles; 
  FILE *fparray;
  FILE *fpRfile;
  
  
  
  /* Open file that contains list of files */
  printf("\n%s\n",argv[1]);  						/*show the filename of list */
  fplistfiles=fopen(argv[1],"r");               	/*open list of files*/
  printf("%s\n", argv[2]);
  z=atoi(argv[2]);
  
  /* Blah bleh bleh */
  for(j=0; j<z; j++)
	{
	  fscanf(fplistfiles,"%s",&filename1);      	/*scant filename*/
	  printf("Read file %s\n",filename1);       	/*showt filename*/
	  fparray=fopen(filename1,"r");             	/*open file*/
	  for (i=0; i<NUM; i++)
		{
		  fscanf(fparray,"%f ",&array[i]);			/*scan data from file */
		  //printf("array:%d, ",array[i]);
		  /* Change each value from level to reflectivity */
		  if ((array[i] > 11.0))
		  {
		  array[i]=11.0;
		  }
		    
		  //if ((array[i] < 5.0)) //|| (avearray[i] > 15.0))	/* Cut junk values */
		  if ((array[i] < 2.0)) //|| (avearray[i] > 15.0))	/* Cut junk values */
		  	{
		  	  Zarray[i]=array[i]*0.0;
		  	}
		  else
		  	{
		  	  Zarray[i]=array[i]*5.0;						/*change to feflectivity*/
		  	}
		  	  	
		  /* Change each value from reflectivity to rain*/
		  if (Zarray[i]!=0.0)
		  {
		    Rarray[i]=(pow((pow(10.0,(Zarray[i]/10.0))/300.0),(1.0/1.4)))/4.0;
		  }
		  else
		  	{
		  	  Rarray[i]=0.0;
  			}
		  
		  addRarray[i]=addRarray[i]+Rarray[i];     	/*add data to accum array*/
		}
	  fclose(fparray);
	}
  fclose(fplistfiles);
  
  /* Calculate average of levels for each cell */
  for (i=0; i<NUM; i++)
  	{
  		Ravearray[i]=addRarray[i]/z;
  	}
  
     
  /* Write new data to new files */
  	fpRfile=fopen("SDUS53_RAIN.txt","w");
    for (m=0; m<NUMr; m++) 							/* NUML - number of lines */
  	{
    	for (n=0; n<NUMc; n++) 						/* NUMC - number of char in line */
  		{
  			fprintf(fpRfile, "%3.3f ", Ravearray[m*NUMc+n]);
  		}	  
  	  	fprintf(fpRfile,"\n");
  	}
  

  return 0;
}

