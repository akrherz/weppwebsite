/********************************************************************
* Program average.c
*
* This program reads four RADAR files and one HRAP file and combine
* them using information from structure.dat file.
*
*                                               MK 28/06/2002
*********************************************************************/


#include<stdio.h>
#include<math.h>
#define rad_ar 214832/*463*464=214832 number of records in each of RADAR files for Iowa area */
#define hrapIO 23182 /*number of records in HRAP file for Iowa area */


float sraRADAR[rad_ar];
float RADAR[rad_ar];              /*RADAR data array*/
float HRAP[hrapIO];               /*HRAP data array*/

main(int argc, char *argv[])
{

  int i,j,x,y,n,no;                 /*loop variables*/
  int nuinarr;                      /*number of record in RADAR array*/
  int nl;
  float sum;                        /*sum of averaging data*/
  float average;                    /*average from RADAR data*/
  FILE *fpw;                        /*file pointer to RADAR data file*/
  FILE *fph;                        /*file pointer to hrap data file*/
  FILE *fpst;                       /* file pointer to file with geometrical
									   structure hrap/RADAR*/

  
  //printf("Convetring to hrap grid...\n");
  

  /*initialization of local variables*/
  
  no=0;
  n=0;
  nuinarr=0;
   

  /* open file that consists structure information*/
  fpst=fopen(argv[1],"r");
  
  /* open hrap file to write average data*/
  
  fph=fopen(argv[3],"r");
  for(j=0; j<134; j++)
  {
  	for(i=0; i<173; i++)
  	{
  		fscanf(fph,"%f", &HRAP[hrapIO-(j+1)*173+i]);
  	}
  }
  fclose(fph);
  fph=fopen(argv[3],"w");
  
  /* open RADAR data files and read it to array RADAR*/
  fpw=fopen(argv[2],"r");
  //printf("%s\n",argv[2]);
  for(j=0; j<463; j++)
  {
  for(i=0; i<463; i++)
	{
	  fscanf(fpw,"%f", &RADAR[(462*463)-(j+1)*463+i]);
	}
	fscanf(fpw,"%f", &sraRADAR[j]);
  }
  
  /*
  for(j=0; j<463; j++)
  {
	for(i=0; i<464; i++)
	{
	  fscanf(fpw,"%f", &RADAR[rad_ar-j*464+i]);
	  printf("%d ",j*464+i);
	}
	printf("\n");
	//fscanf(fpw,"%f", &sraRADAR[j]);
  }*/
  
  
  /*read information from structure.dat file and use it to count
	average from RADAR data files                                  */
  fscanf(fpst,"%d", &nl);
  for(j=0; j<nl; j++)
	{

	  fscanf(fpst,"%d",&no);

	  fscanf(fpst,"%d",&n);
	  sum=0.0;

	  for(i=0; i<n; i++)
		{
		  fscanf(fpst,"%d", &nuinarr);
		  sum=sum+RADAR[nuinarr];
		}
	  average=sum/n;
	/*if there is non-zero value in the HRAP array then average values*/
	  if ((HRAP[no] > 0)&&(average > 0))
		{
			if (HRAP[no]>average){
				HRAP[no]=average;
			}
		}		
	/*if there is 0 in the HRAP array then put there calculated radar value*/
	  if ((HRAP[no]==0)&&(average > 0))
	  	{
	  		HRAP[no]=average;
	  	}
	
	}

  /*print average values to file*/

  for(x=0; x<134; x++)
	{
	  for(y=0; y<173; y++)
		{
		  fprintf(fph,"%3.3f ",HRAP[(134-1-x)*173+y]);
		}
	  fprintf(fph,"\n");
	}

  
  /*close opened file*/
  fclose(fpw);
  fclose(fph);
  fclose(fpst);
  
  return 0;
}
