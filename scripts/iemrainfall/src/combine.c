/***********************************************************************
 *
 * program combine.c
 *
 * Program for calibrating WSI data usin data fron NWS
 *
 * This program reads data from four files (for 15, 30, 45, 60 min in
 * hour) and multiplies them by weight is result of comaring these data
 * with data from NWS.
 *                                                            M.K 3/6/02
 * 26 May 2004	Looked it over.  Looks good -DEH
 ***********************************************************************/


#include<stdio.h>
#define NUM 23182 /*Number of records in files */
#define NUMc 173  /*Number of columns in files */
#define NUMr 134  /*Number of rows in files */

float WSIarr1[NUM], WSIarr2[NUM], WSIarr3[NUM], WSIarr4[NUM], NWSarr[NUM];

main()
{


  int j, i, m, n;
  char filenameNWS[40];
  char filenameWSI1[40], filenameWSI2[40], filenameWSI3[40], filenameWSI4[40];
  char filenameOUT1[40], filenameOUT2[40], filenameOUT3[40], filenameOUT4[40];

  float WSIhouracc,weight;
  FILE *fplstWSI, *fplstNWS, *fplstOUT, *fpNWS;
  FILE *fpWSI1, *fpWSI2, *fpWSI3, *fpWSI4;
  FILE *fpOUT1, *fpOUT2, *fpOUT3, *fpOUT4;


  /* open list of NWS files */
  fplstNWS=fopen("../tmp/S4_files.dat","r");

  /* open list of output files */
  fplstOUT=fopen("../tmp/combout.dat","r");


  /* open list of WSI files */
  fplstWSI=fopen("../tmp/NEX_files.dat","r");

  for (j=0; j<1; j++)
	{
	  /*printf("%d\n ",j);*/
	  /*************************************************
	   * take from the list and open four files from   *
	   * WSI files list and one from NWS files list    *
	   *************************************************/

	  fscanf(fplstWSI,"%s",&filenameWSI1);
	  fpWSI1=fopen(filenameWSI1,"r");

	  fscanf(fplstWSI,"%s",&filenameWSI2);
	  fpWSI2=fopen(filenameWSI2,"r");

	  fscanf(fplstWSI,"%s",&filenameWSI3);
	  fpWSI3=fopen(filenameWSI3,"r");

	  fscanf(fplstWSI,"%s",&filenameWSI4);
	  fpWSI4=fopen(filenameWSI4,"r");



	  fscanf(fplstOUT,"%s",&filenameOUT1);
	  fpOUT1=fopen(filenameOUT1,"w");

	  fscanf(fplstOUT,"%s",&filenameOUT2);
	  fpOUT2=fopen(filenameOUT2,"w");

	  fscanf(fplstOUT,"%s",&filenameOUT3);
	  fpOUT3=fopen(filenameOUT3,"w");

	  fscanf(fplstOUT,"%s",&filenameOUT4);
	  fpOUT4=fopen(filenameOUT4,"w");


	  fscanf(fplstNWS,"%s",&filenameNWS);
	  fpNWS=fopen(filenameNWS,"r");
	  /*printf("%s,%s,%s,%s,%s\n ", filenameWSI1, filenameWSI2, filenameWSI3, filenameWSI4, filenameNWS);*/

	  /*******************************
	   * read opened files to arrays *
	   *******************************/


	  for (i=0; i<NUM; i++)
		{
		  fscanf(fpWSI1,"%f",&WSIarr1[i]);

		  fscanf(fpWSI2,"%f",&WSIarr2[i]);

		  fscanf(fpWSI3,"%f",&WSIarr3[i]);

		  fscanf(fpWSI4,"%f",&WSIarr4[i]);

		  fscanf(fpNWS,"%f",&NWSarr[i]);

		  /*************************************
		   * calibrate WSI data using NWS data *
		   *************************************/
		  weight=0.0;
		  WSIhouracc=WSIarr1[i]+WSIarr2[i]+WSIarr3[i]+WSIarr4[i];
		  /*printf("i=%d\n ",i);
			printf("%f+%f+%f+%f=%f NWS=%f ",WSIarr1[i],WSIarr2[i], WSIarr3[i], WSIarr4[i], WSIhouracc,NWSarr[i]);*/
		  if ((WSIhouracc==0.0) && (NWSarr[i]==0.0))
			{
			  weight=0.0;
			}
		  if ((WSIhouracc!=0.0) && (NWSarr[i]==0.0))
			{
			  weight=0.0;
			}
		  /** This divides up the NCEP accumulation into 4 equal bins */
		  if ((WSIhouracc==0.0) && (NWSarr[i]!=0.0))
			{
			  WSIarr1[i]=NWSarr[i]/4;
			  WSIarr2[i]=NWSarr[i]/4;
			  WSIarr3[i]=NWSarr[i]/4;
			  WSIarr4[i]=NWSarr[i]/4;
			  weight=1.0;
			}
		  /** Linearly scale the NEXRAD accumulations */
		  if ((WSIhouracc!=0.0) && (NWSarr[i]!=0.0))
			{
			  weight=NWSarr[i]/WSIhouracc;
			}

		  WSIarr1[i]=WSIarr1[i]*weight;
		  WSIarr2[i]=WSIarr2[i]*weight;
		  WSIarr3[i]=WSIarr3[i]*weight;
		  WSIarr4[i]=WSIarr4[i]*weight;
		  /*printf(" w=%f\n",weight);
			printf("i=%d %f %f %f %f\n\n",i,WSIarr1[i],WSIarr2[i], WSIarr3[i], WSIarr4[i]);*/
		}



	  /***************************
	   * write new data to files *
	   ***************************/
	  fclose(fpNWS);
	  fclose(fpWSI1);
	  fclose(fpWSI2);
	  fclose(fpWSI3);
	  fclose(fpWSI4);




	  for (m=0; m<NUMr; m++) /* NUML - number of lines */
		{
		  for (n=0; n<NUMc; n++) /* NUMC - number of characters in each line */
			{
			 fprintf(fpOUT1, "%3.3f ", WSIarr1[m*NUMc+n]);
			 fprintf(fpOUT2, "%3.3f ", WSIarr2[m*NUMc+n]);
			 fprintf(fpOUT3, "%3.3f ", WSIarr3[m*NUMc+n]);
			 fprintf(fpOUT4, "%3.3f ", WSIarr4[m*NUMc+n]);
			}
		  fprintf(fpOUT1,"\n");
		  fprintf(fpOUT2,"\n");
		  fprintf(fpOUT3,"\n");
		  fprintf(fpOUT4,"\n");

		}



	  /*******************
	   * close all files *
	   *******************/
	  //DEH
	  //fclose(fpNWS);
	  fclose(fpOUT1);
	  fclose(fpOUT2);
	  fclose(fpOUT3);
	  fclose(fpOUT4);

	}
  fclose(fplstWSI);
  fclose(fplstNWS);


  return 0;
}
