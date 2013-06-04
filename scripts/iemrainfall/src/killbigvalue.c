/***********************************************************************
 *
 * program killbigvalue.c
 * 
 * This programm changes too big values of precipitation to 0.
 *
 *                                                           M.K 23/11/02
 ***********************************************************************/

#include<stdio.h>
#include<math.h>
#define NUM 23182 /*Number of records in files */
#define NUMc 173  /*Number of columns in files */
#define NUMr 134  /*Number of rows in files */


main(int argc, char *argv[])
{
  

  int j, i, m, n, z;
  char num[1];
  char filename1[40], filename2[40], filename3[40], filename4[40];
  FILE *fplistfiles, *fparray, *fpaccum, *fperror;
  float array[23182]={0.0}, addarray[23182]={0.0};
  
  
  
  /* Open passedfile  */
  
      
  for(j=0; j<24; j++)
	{
	  	  
	  fparray=fopen(argv[1],"r");             /*open file*/
	  
	  
	  for (i=0; i<23182; i++)
		{
		  fscanf(fparray,"%f ",&array[i]);      /*scan data from file */

		  if (array[i] > 125)  /* Nothing over 5 inch per hour, 1e6 */
			  {
				
				array[i]=0;
			  }
		}
	  
	}
  fclose(fparray);
  fparray=fopen(argv[1],"w");  
  /*write data to file*/
  for (m=0; m<NUMr; m++) /* NUML - number of lines */
	{
	  for (n=0; n<NUMc; n++) /* NUMC - number of characters in each line */
		{
		  fprintf(fparray, "%f ", array[m*NUMc+n]);
		  
		}	  
		  fprintf(fparray,"\n");
	}  

  fclose(fparray);
  return 0;
}
