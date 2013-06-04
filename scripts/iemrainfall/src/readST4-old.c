/***********************************************************************
 *
 * program readST2.c
 * 
 * Program for NCEP stage 4 files in binary 
 *
 * This program read data from specific file and print them out to
 * file outIowa.dat in array 174 x 134.
 *                                                           M.K 5/4/03
 ***********************************************************************/

#include<stdio.h>
#define nc 987601
float farray[nc]={0.0}, harray[nc]={0.0};


main(int argc, char *argv[])

{
  int x,y,j,i,l,m,k,n,cnt;  
  FILE *fp1, *fp2, *fp3;
  
  
  

  /******************/  
  /*open binary file*/
  /******************/  

  fp1=fopen(argv[1],"rb");



  /********************/  
  /*read data to array*/
  /********************/  

  cnt=fread(farray, sizeof(float), nc, fp1);
  /*  printf("read %d characters\n",cnt);*/
    


  /****************************************/
  /* Print to file data for Iowa          */
  /* 134 lines (each line has 173 values) */
  /****************************************/
  
  /*Array is flipped, so print it to file from the last line*/


  /*printf("Printing data to file outIowa.dat...\n");*/

  i=0;
  j=0;
  k=0;
  


  fp3=fopen("outIowa.dat","w");
  
  /* We start on line 448, column 589 */
  j=520269; /*Jump to the first character in last line for Iowa*/
    for (k=0; k<134; k++) /*Iowa area consists 134 lines*/
	{
	  for (i=0; i<173; i++) /*Each line for Iowa consists 173 characters*/
		{
		  fprintf(fp3, "%f ", farray[j+i]);
		}	  
	  fprintf(fp3,"\n");
	  j=j+1160; /*Jump to the begining of previous line*/

  	}
  
		  
				  
  /*************/  
  /*close files*/
  /*************/

  fclose(fp1);
  fclose(fp3);
  
  /*fclose(fp2);*/
  
  

  return 0;
}

