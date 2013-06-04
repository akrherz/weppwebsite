/****************************************************************
	This is the program to decompress raster Level III NEXRAD 
	data from RLE format.

	usage: ./read_raster_RLE.exe input_file > output_file

              June 27, 2003, michal-kraszewski@uiowa.edu
*****************************************************************/

#include <stdio.h>
main( int argc, char **argv )
{
	FILE *ifile;
   	unsigned char in[1000000];
	unsigned int insize;
	int nr,i,z,m,j,k,chunks,deli,mode;
	float angle, delta;

/**************************************************
	Open and read file into array                  
***************************************************/
ifile = fopen( argv[1], "rb" );
if( ifile == NULL ) exit( 1 );
insize = fread( in, 1, 100000, ifile );

/**************************************************
Get mode information :
0=Maintenance, 
1=Clear air, 
2=Precipitation/Severe weather
***************************************************/

mode=in[87];
if ((mode==0)||(mode==1))
	{
		exit(1);
	}

/**************************************************
	Find the begining of data coded with hex BA 07
	of BA 0F and write header information to file
***************************************************/


printf("# %s\n",argv[1]);
printf("# Readed bytes: \t%d",insize);
m=0;
for (i=0; i<insize; i++)
{
if ((in[i]==186)&(in[i+1]==7))
	{
		m=i+2;
		printf("\n# Code BA O7 : \t%d\t%d\t(as %dth byte and %dth byte)\n",in[m-2],in[m-1],m-2,m-1);
	}
if ((in[i]==186)&(in[i+1]==15))
	{
		m=i+2;
		printf("\n# Code BA OF : \t%d\t%d\t(as %dth byte and %dth byte)\n",in[m-2],in[m-1],m-2,m-1);
	}	
}
if ((m==0))
{
	printf("\n# Code BA OF or BA 07 has not been found...\n");
	exit (1);
}


printf("# Header information:\n");
printf("# I start coordinate : %d\n",in[m+4]*255+in[m+5]);
printf("# J start coordinate : %d\n",in[m+6]*255+in[m+7]);
printf("# X scale : %d\n",in[m+8]*255+in[m+9]);
printf("# Y scale : %d\n",in[m+10]*255+in[m+11]);
printf("# X scale : %d\n",in[m+12]*255+in[m+13]);
printf("# Y scale : %d\n",in[m+14]*255+in[m+15]);
printf("# Number of rows : %d\n",in[m+16]*255+in[m+17]);
nr=in[m+16]*255+in[m+17];
printf("# Packing descriptor : %d",in[m+18]*255+in[m+19]);
printf("\n");

/**************************************************
	Decompress RLE
***************************************************/
m=m+20;
for (z=0; z<nr; z++)                     //nr is no of rows
{
	
	chunks=(in[m]*255+in[m+1]);          //no of chunks in row
	for (i=0; i<chunks; i++)             //for no of bytes
	{
		for (j=0; j<in[m+i+2]>>4; j++)   //first 4 bits of byte
		{
			printf("%d ",in[m+i+2]&15);  //second 4 bits of byte
		}
	}
	printf("\n");
	m=m+chunks+2;                        //set m to next azimuth
}

fclose(ifile);
exit( 0 );

}

