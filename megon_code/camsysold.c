#define _BSD_SOURCE
#include <stdio.h>
#include <assert.h>
#include <unistd.h>
#include <stdlib.h>
#include <libssh/libssh.h>
#include <string.h>
#include <time.h>

//-------------------function checks if any odb value is too large, if so changes them and reports back-----------------
void odb_value_check(int num_photos,double exposure_time,int light,int led_intensity){
   char odb_error[1000] = "";
   int odb_error_started = 0;

   if (num_photos > 8) {
      num_photos = 8;
      system("odbedit -c 'set \"Equipment/Target_Camera/Variables/num_photos\" 8'");
      strcpy(odb_error,  "WARNING : num photos cap = 8;\n ");
      odb_error_started = 1;
   }

   if (exposure_time > 5000000) {
      exposure_time = 500000;
      system("odbedit -c 'set \"Equipment/Target_Camera/Variables/exposure_time\" 2'");
      if (odb_error_started ==0){
         strcpy(odb_error, "WARNING: exposure cap = 2s;\n ");
         int odb_error_started = 1;
      }
      if (odb_error_started ==1){
         char exposure_error[100]= "exposure cap = 2s;\n "; 
         strcat(odb_error,exposure_error);
      }
   }
      
   if ((light > 3) || ( light < 0 )) {
      light = 1;
      system("odbedit -c 'set \"Equipment/Target_Camera/Variables/light\" 1'");
      if (odb_error_started ==0){
         strcpy(odb_error,"WARNING: light = 1 or 2; ");
         int odb_error_started = 1;
      }
      if (odb_error_started ==1) strcat(odb_error, " light = 1 or 2; ");
   }
   
   if ((led_intensity > 10) || (led_intensity) < 0) {
      led_intensity = 10;
      system("odbedit -c 'set \"Equipment/Target_Camera/Variables/led_intensity\" 10'");
      if (odb_error_started ==0){
         strcpy(odb_error, "WARNING: LED Int cap = 10; ");
         int odb_error_started = 1;
      }
      if (odb_error_started ==1) strcat(odb_error, "LED Int cap = 10; ");
   }

   printf("ODB Warnings: %s\n", odb_error);
   system(("odbedit -c 'set \"Equipment/Target_Camera/Settings/odb_error\" %s'", odb_error));
}

//------------------------function to free an ssh channel--------------------------------------
void free_channel(ssh_channel channel) {
    //ending channel
    ssh_channel_send_eof(channel);
    ssh_channel_close(channel);
    ssh_channel_free(channel);
}


//------------------------function to free an ssh session--------------------------------------
void free_session(ssh_session session) {
    //ending sesion
    ssh_disconnect(session);
    ssh_free(session);
}


//------------------------function to handle an ssh error--------------------------------------
void error(ssh_session session) {
    fprintf(stderr, "Error: %s\n", ssh_get_error(session));
    free_session(session);
    exit(-1);
}

//---------------------------function that is the guts of the program--------------------------
//  contain all of the ssh connections, 
//          all of the commands to be sent to the rpi and the dell, 
//          the hostnames, usersnames and the number of photos
int ssh_light(char* hostname_pi, char* user_pi, char* password_pi, char* pi_led_command, 
              char* initial_pi_check_command, char* hostname_dell, char* user_dell, char* password_dell, 
              char* dell_image_command, char* dell_dark_command, int ODB_number_photos) {

//--initializing session and channel for pi and dell
   printf("\nStarting connections to pi and dell\n");
   ssh_session session_pi;
   ssh_channel channel_pi;
   ssh_session session_dell;
   ssh_channel channel_dell;
   int rc_pi, port_pi = 22;
   int rc_dell, port_dell = 22;
   char buffer_dell_analysis[1024] = "";
   char buffer_dell[1024] = "";
   char buffer_pi[1024];
   unsigned int nbytes_pi;
   unsigned int nbytes_dell;
   double values[15];
   FILE *b = fopen("/home/meg/online/web/mhttpd/readout.txt", "w");
   char clear[] = "";
   fprintf(b, "");
   fclose(b);

   char myTxt[100];
   FILE *out = fopen("/home/meg/online/web/mhttpd/readout.txt", "a");
   //myTxt[0] = 0;
   sprintf(myTxt, "Start of Image Sequence:%d",(int)time(NULL) );
   strcat(myTxt, "\n");
   fprintf(out, "%s", myTxt);
   fclose(out);
   session_pi = ssh_new();
   if (session_pi == NULL) exit(-1);
   session_dell = ssh_new();
   if (session_dell == NULL) exit(-1);
   
//--starting session with pi
   ssh_options_set(session_pi, SSH_OPTIONS_HOST, hostname_pi); 
   ssh_options_set(session_pi, SSH_OPTIONS_PORT, &port_pi);
   ssh_options_set(session_pi, SSH_OPTIONS_USER, user_pi);
   
//--starting session with dell
   ssh_options_set(session_dell, SSH_OPTIONS_HOST, hostname_dell); 
   ssh_options_set(session_dell, SSH_OPTIONS_PORT, &port_dell);
   ssh_options_set(session_dell, SSH_OPTIONS_USER, user_dell);
   
   rc_dell = ssh_connect(session_dell);
   if (rc_dell != SSH_OK) error(session_dell);
   
   rc_dell = ssh_userauth_password(session_dell, NULL, password_dell);
   if (rc_dell != SSH_AUTH_SUCCESS) error(session_dell);
   
//--open new channel and session
   //channel_dell = ssh_channel_new(session_dell); 
   //if (channel_dell == NULL) exit(-1);
   //rc_dell = ssh_channel_open_session(channel_dell);

   channel_dell = ssh_channel_new(session_dell);
   rc_dell = ssh_channel_open_session(channel_dell);
//--get the darkfield image
   nbytes_dell =0;
   printf("Executing '%s'\n", dell_dark_command); 
   rc_dell = ssh_channel_request_exec(channel_dell, dell_dark_command); // Takes a single darkfield image
   printf("Print of dell dark output:\n");
   nbytes_dell = ssh_channel_read(channel_dell, buffer_dell, sizeof(buffer_dell), 0);
   nbytes_dell = 0;
//--loop here writes out the ssh output(stdout) to buffer_dell
   /*
   while (nbytes_dell > 0) {
      fwrite(buffer_dell, 1, nbytes_dell, stdout);
      nbytes_dell = ssh_channel_read(channel_dell, buffer_dell, sizeof(buffer_dell), 0);
   }
   */
   //printf("now have readout from df\n");
   char * pch3 = strtok(buffer_dell, ":");
   char darkfieldimg[]= "";
   strcpy(darkfieldimg, pch3);
   FILE *out2 = fopen("/home/meg/online/web/mhttpd/readout.txt", "a");
   myTxt[0] = 0;
   strcpy(myTxt, "");
   sprintf(myTxt, "Darkfield Image- %s Captured:%d", buffer_dell, (int)time(NULL));
   strcat(myTxt, "\n");
   fprintf(out2, "%s", myTxt);
   fclose(out2);

   channel_dell = ssh_channel_new(session_dell);
   rc_dell = ssh_channel_open_session(channel_dell);
    
//--Connects to pi for LED script
   rc_pi = ssh_connect(session_pi);
   if (rc_pi != SSH_OK) error(session_pi);

//--authenticating pi
   rc_pi = ssh_userauth_password(session_pi, NULL, password_pi); 
   if (rc_pi != SSH_AUTH_SUCCESS) error(session_pi);

//--opening channel with pi
   channel_pi = ssh_channel_new(session_pi); 
   if (channel_pi == NULL) exit(-1);
   
//--opening session with pi
   rc_pi = ssh_channel_open_session(channel_pi); 
   if (rc_pi != SSH_OK) error(session_pi);
   
//--runs led_check
   printf("\nExecuting '%s'\n", initial_pi_check_command);
   rc_pi = ssh_channel_request_exec(channel_pi, initial_pi_check_command); 
   nbytes_pi = ssh_channel_read(channel_pi, buffer_pi, sizeof(buffer_pi), 0);
   nbytes_pi=0;
//--reads out led_check output to buffer_pi
   while (nbytes_pi > 0) { 
      fwrite(buffer_pi, 1, nbytes_pi, stdout);
      nbytes_pi = ssh_channel_read(channel_pi, buffer_pi, sizeof(buffer_pi), 0);
   }
   // printf("about to parse led_check\n");
//--parses the output of led_check command
   char * wait_time =strtok(buffer_pi, ":");
   int wait_time_int = 0;
   long int start_time = 0;
   wait_time = strtok(NULL, ":");
   wait_time_int = atoi(wait_time);
   wait_time =strtok(NULL, ":");
   start_time = strtod(wait_time, NULL);
   start_time = (int)time(NULL) + wait_time_int;
   //start_time = 0;
   //wait_time_int=0;
   printf("here is wait_time %d\n", wait_time_int);
   printf("here is start_time %ld\n", start_time);
   strcpy(buffer_pi, "");
   FILE *out3 = fopen("/home/meg/online/web/mhttpd/readout.txt", "a");
   //myTxt[0] = 0;
   strcpy(myTxt, "");
   sprintf(myTxt, "Light will turn on in %d seconds:%d", wait_time_int, start_time);
   strcat(myTxt, "\n");
   fprintf(out3, "%s", myTxt);
   fclose(out3);


      
//--reads out the error from led_check to buffer_pi
   /*
   nbytes_pi = ssh_channel_read(channel_pi, buffer_pi, sizeof(buffer_pi), 1); 
  
   while (nbytes_pi > 0) {
      fwrite(buffer_pi, 1, nbytes_pi, stdout);
      nbytes_pi = ssh_channel_read(channel_pi, buffer_pi, sizeof(buffer_pi), 1);
   }
   */
   FILE *f = fopen("/home/meg/online/web/mhttpd/lighttime.txt", "w");
   fprintf(f, "%ld,%d", start_time, wait_time_int);
   fclose(f);
//--puts the error/wait time/start time from led_check in the ODB
   char led_error[1024] = "";
   //strcpy(led_error,buffer_pi);
   char odb_command[1024] = "";
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Settings/led_error\" %s'", led_error);
   system(odb_command);
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Variables/start_time\" %i'", start_time);
   system(odb_command);
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Variables/wait_time\" %i'", wait_time_int);
   system(odb_command);
//   sleep(wait_time_int);   
   time_t rawtime;
   struct tm * timeinfo;
   printf("LED not available yet, sleeping for %i \n\n",wait_time_int);
   time ( &rawtime );
   timeinfo = localtime ( &rawtime );
   //sleep(wait_time_int);//waits until LED is available then continues script
   time ( &rawtime );
   timeinfo = localtime ( &rawtime );
   
//--Connects to pi to turn on LED when available
   //ssh_channel channel_pi2;
   channel_pi = ssh_channel_new(session_pi);      //--opening channel with pi
   rc_pi = ssh_channel_open_session(channel_pi);  //--opening session with pi
   rc_pi = ssh_channel_request_exec(channel_pi, pi_led_command); //--execute command to turn on light when allowed
   if (rc_pi != SSH_OK) error(session_pi);   

//--Initializing image names
//  currently holds all image names seperately then uses these in aalysis commands
   char *all_image_names[ODB_number_photos]; //--array to hold multiple single image names of characters
   char image_error[1024] = "";
   char image_name[1024] = "";
   char image_name1[1024] = "";
   char image_name2[1024] = "";
   char image_name3[1024] = "";
   char image_name4[1024] = "";
   char image_name5[1024] = "";
   char image_name6[1024] = "";
   char image_name7[1024] = "";
   char image_name8[1024] = "";
   
//--takes all photos and prints output from dell
   for (int j = 0; j< ODB_number_photos; j++){ 
     
      channel_dell = ssh_channel_new(session_dell);
      rc_dell = ssh_channel_open_session(channel_dell);
      int nbytes_dell_test = 0;
      char buffer_dell_test[1024]= "";
      rc_dell = ssh_channel_request_exec(channel_dell, dell_image_command); //--executes command to take photos
      printf("Executing '%s'\n", dell_image_command);      
      printf("Print of dell image output:\n\n=====================================\n");
      nbytes_dell_test = ssh_channel_read(channel_dell, buffer_dell_test, sizeof(buffer_dell_test), 0);
      nbytes_dell=0;
//--writes ouput to buffer_dell
      while (nbytes_dell_test > 0) {
         fwrite(buffer_dell_test, 1, nbytes_dell_test, stdout);
         nbytes_dell_test= ssh_channel_read(channel_dell, buffer_dell_test, sizeof(buffer_dell_test), 0);
      }
      
//--grabs the image names from dell output and saves them for analysis
      char * pch2 = strtok(buffer_dell_test, ":");

      FILE *out4 = fopen("/home/meg/online/web/mhttpd/readout.txt", "a");
      myTxt[0] = 0;
      strcpy(myTxt, "");
      sprintf(myTxt, "Image %d- %s Captured:%d",j+1, pch2, (int)time(NULL));
      strcat(myTxt, "\n");
      fprintf(out4, "%s", myTxt);
      fclose(out4);
      if (j ==0) strcpy(image_name, pch2);
      if (j ==1) strcpy(image_name1, pch2);
      if (j ==2) strcpy(image_name2, pch2);
      if (j ==3) strcpy(image_name3, pch2);
      if (j ==4) strcpy(image_name4, pch2);
      if (j ==0) printf("Image_name -  %s \n=====================================\n\n", image_name);
      if (j ==1) printf("Image_name -  %s \n=====================================\n\n", image_name1);
      if (j ==2) printf("Image_name -  %s \n=====================================\n\n", image_name2);
      if (j ==3) printf("Image_name -  %s \n=====================================\n\n", image_name3);
      if (j ==4) printf("Image_name -  %s \n=====================================\n\n", image_name4);




      strcpy(buffer_dell_test, "");
      
      /// nbytes_dell = ssh_channel_read(channel_dell, buffer_dell, sizeof(buffer_dell), 1);
      //while (nbytes_dell > 0) {//writes error outputs to buffer_dell
      //   fwrite(buffer_dell, 1, nbytes_dell, stdout);
      //   nbytes_dell = ssh_channel_read(channel_dell, buffer_dell, sizeof(buffer_dell), 1);
      //}
      //printf("Capture_images.py errors: %s\n\n", buffer_dell);
      //strcpy(image_error, buffer_dell);
      //printf("image_error: %s", image_error);
      //channel_dell = ssh_channel_new(session_dell);
      //rc_dell = ssh_channel_open_session(channel_dell);
   }
   FILE *d = fopen("/home/meg/online/web/mhttpd/imagename.txt", "w");
   fprintf(d, "%s", image_name);
   fclose(d);
//--writes last image name to odb and error
// sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Settings/image_error\" %s'", image_error);
// system(odb_command);
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Settings/image_name\" %s'", image_name);
   system(odb_command);
      
   ssh_disconnect(session_pi);
   
//--creating analysis commands using image names and executing
   char dell_analysis_command[100];
   printf("\n---ANALYSIS---\n");
   
//--executes command to take photos THIS SEEMS TO BE COMMAND TO ANALYZE PHOTOS
   for (int j = 0; j<= ODB_number_photos -1 ; j++){ 
     //channel_dell = ssh_channel_new(session_dell);
     //rc_dell = ssh_channel_open_session(channel_dell); 
     channel_dell = ssh_channel_new(session_dell);
     rc_dell = ssh_channel_open_session(channel_dell);
     printf("\nAnalysis running on image # %i \n", j+1);
     if (j ==0) sprintf(dell_analysis_command, "python3 flip_residue.py %s %s 85 51.61", image_name,image_name);
      if (j ==1) sprintf(dell_analysis_command, "python3 flip_residue.py %s %s 85 51.61", image_name1, image_name1);
      if (j ==2) sprintf(dell_analysis_command, "python3 flip_residue.py %s %s 85 51.61", image_name2, image_name2);
      if (j ==3) sprintf(dell_analysis_command, "python3 flip_residue.py %s %s 85 51.61", image_name3, image_name3);
      if (j ==4) sprintf(dell_analysis_command, "python3 flip_residue.py %s %s 85 51.61", image_name3, image_name3);
      int nbytes_dell_test2 = 0;
      char buffer_dell_test2[1024]= "";
      printf("Executing '%s'\n", dell_analysis_command);
      FILE *out5 = fopen("/home/meg/online/web/mhttpd/readout.txt", "a");
      //myTxt[0] = 0;
      strcpy(myTxt, "");
      sprintf(myTxt, "Executing analysis on image %d:%d", j+1, (int)time(NULL));
      strcat(myTxt, "\n");
      fprintf(out5, "%s", myTxt);
      fclose(out5);
      //strcpy(buffer_dell, "");
      //channel_dell = ssh_channel_new(session_dell);
      //rc_dell = ssh_channel_open_session(channel_dell);
      rc_dell = ssh_channel_request_exec(channel_dell, dell_analysis_command);
      strcpy(dell_analysis_command, "");
      printf("Print of dell analysis output:\n=====================================\n");
      
      nbytes_dell_test2 = ssh_channel_read(channel_dell, buffer_dell_test2, sizeof(buffer_dell_test2), 0); // reading analysis output
      while (nbytes_dell_test2 > 0) {
         fwrite(buffer_dell_test2, 1, nbytes_dell_test2, stdout);
         nbytes_dell_test2 = ssh_channel_read(channel_dell, buffer_dell_test2, sizeof(buffer_dell_test2), 0);
      }
      printf("=====================================\nEnd Analysis \n");
      //channel_dell = ssh_channel_new(session_dell);
      //rc_dell = ssh_channel_open_session(channel_dell);
   
      if (strlen(buffer_dell_test2) != 0){
	printf("now inside\n");
	printf("%i",strlen(buffer_dell_test2));
//--sending analysis error to odb (BUNCH OF COMMENTED OUT CODE MOVED TO END)
      char analysis_error[1024] = "";
      char analysis_output[1024] = "";
      //strcpy(analysis_output,""); 
      strcpy(analysis_output,buffer_dell_test2); 
      //ssh_disconnect(session_dell);
      //printf("here is analysis_output %s", analysis_output);
      char test[6];
      char badchar[]=":";
      for (int i= 0; i< sizeof(analysis_output); i++)
      { 
         if( (analysis_output[i]) == ':') {
            for (int j= 0; j<6; j++){
               test[j] = analysis_output[i+j];
            }
            //  printf("string from for loop is %s\n",test);
         }
      }
      
//--Parsing analysis output of last image
      char * pch = strstr(buffer_dell_test2,"Total Chi:"); //cutting analysis string
      pch = strtok (pch,":");
      int index = 0;
      printf ("%s\n",pch);
      while (pch != NULL)
      {
         pch = strtok (NULL, ":");
         if (pch==NULL) break;
         if (index%2!=0)printf ("%s\n",pch);
         if (index %2 == 0){
            values[index] =atof(pch);
            printf("%f\n",values[index]);
         }
         if (index >13)break;
         index++;
      }
      if (values[0] < 12 && values[0] > 1){
         FILE *out6 = fopen("/home/meg/online/web/mhttpd/readout.txt", "a");
         myTxt[0] = 0;
         strcpy(myTxt, "");
         sprintf(myTxt, "Analysis on image %d was sucessful, analysis results uploaded to webpage and ODB:%d",j+1, (int)time(NULL));
         strcat(myTxt, "\n");
         fprintf(out6, "%s", myTxt);
         fclose(out6);
         break;
      }

   }  
   }
   
   FILE *g = fopen("/home/meg/online/web/mhttpd/cameradata.txt", "w");
   fprintf(g, "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f", values[8], values[10], values[12], values[2], values[4], values[6], values[14], values[0]);
   fclose(g);
   
//--Uploading values to ODB
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Variables/chi\" %.2f'", values[0]);
   system(odb_command);
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Variables/delta_theta(mrad)\" %.1f'", values[2]);
   system(odb_command);
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Variables/delta_phi(mrad)\" %.1f'", values[4]);
   system(odb_command);
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Variables/delta_psi(mrad)\" %.1f'", values[6]);
   system(odb_command);
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Variables/delta_x(um)\" %.0f'", values[8]);
   system(odb_command);
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Variables/delta_y(um)\" %.0f'", values[10]);
   system(odb_command);
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Variables/delta_z(um)\" %.0f'", values[12]);
   system(odb_command);
   sprintf(odb_command,"odbedit -c 'set \"Equipment/Target_Camera/Variables/bowing_parameter(um)\" %.0f'", values[14]);
   system(odb_command);
   
   return 1;
   }

//--function needed to get odb values in C script
char* grab_odb(char* odb_command){
   FILE *fp,*outputfile;
   char var[40];
   char test[1024] = "";
   //printf("about to popen");
   fp = popen(odb_command, "r");
   //printf("popen done");
   while (fgets(var, sizeof(var), fp) != NULL) 
   {
      strcat(test,var);
   }
   pclose(fp);
   //printf(test);
   return test;
}

//--main program 
int main(){
   int run_number = 0;
   while(1){
//--grabbing odb parameters
      printf("\n\n\n RUN NUMBER - %i\n\n", ++run_number);
      int num_photos = atoi(grab_odb("odbedit -c 'ls -v \"Equipment/Target_Camera/Variables/num_photos\"'"));
      int cycle_time = atoi(grab_odb("odbedit -c 'ls -v \"Equipment/Target_Camera/Variables/cycle_time\"'"));
      double exposure_time = strtod(grab_odb("odbedit -c 'ls -v \"Equipment/Target_Camera/Variables/exposure_time\"'"),NULL);
      int led_intensity = atoi(grab_odb("odbedit -c 'ls -v \"Equipment/Target_Camera/Variables/led_intensity\"'"));
      int light = atoi(grab_odb("odbedit -c 'ls -v \"Equipment/Target_Camera/Variables/light\"'"));
      int initiate_while = 1;
      int exposure = exposure_time;
      int ODB_start_stop;
      int led_ontime = num_photos*7;
      int button = 1;
      int insertion = 0;
      int extraction = 0;
      FILE *f = fopen("/home/meg/online/web/mhttpd/camerasettings.txt", "w");
      fprintf(f, "%d,%d,%d,%d,%d,%d", exposure, num_photos, cycle_time, led_intensity, light,button );
      fclose(f);
//--printing out grabbed odb parameters
      printf("Ontime - %i\n", led_ontime);
      printf("LED Intensity - %i\n", led_intensity);
      printf("Light Number - %i\n", light);
      printf("Number photos - %i\n", num_photos);
      printf("Exposure Time - %f\n",exposure_time);
      
//--checking odb values
      odb_value_check(num_photos,exposure_time,light,led_intensity);
      
//--creating the commands to be send to dell and rpi using grabbed odb parameters
      char pi_led_command[1024];
      sprintf(pi_led_command, "python3 uci_led_turn_on.py %i %i %i 1 1", light, led_ontime, led_intensity); 

      //>>>>>>this needs to include our lights script 3 parameters

      char initial_pi_check_command[1024]; 
      sprintf(initial_pi_check_command, "python3 uci_led_check.py %i %i %i 1 1", light, led_ontime, led_intensity);
      char dell_dark_command[1024];
      sprintf(dell_dark_command, "python3 darkfield.py 3856 2764 1 %i 200", exposure);//"python darkfield.py %f",exposure_time);
      char dell_image_command[1024];
      sprintf(dell_image_command, "python3 test.py 3856 2764 1 %i 200", exposure);// %f", exposure_time);
      
//--sends all the commands and hostnames etc to function to execute commands
      ssh_light("129.129.143.203", "pi", "muegamma",pi_led_command, initial_pi_check_command, "129.129.143.189", "ucicam", "muegamma", 
                dell_image_command, dell_dark_command, num_photos);
      char myTxt[100];
//--below allows the process to start and stop, if start and stop are not applied it will wait the cycle time
      initiate_while =0;
      printf("Cycle time: %i\n",cycle_time);
      FILE *out7 = fopen("/home/meg/online/web/mhttpd/readout.txt", "a");
      myTxt[0] = 0;
      strcpy(myTxt, "");
      sprintf(myTxt, "Entering wait time of %d:%d",cycle_time, (int)time(NULL));
      strcat(myTxt, "\n");
      fprintf(out7, "%s", myTxt);
      fclose(out7);      
//--this finds stop requested by odb and sets value back to 0, then starts search for start
      for(int j=1; j<cycle_time; j++) {
         ODB_start_stop = atoi(grab_odb("odbedit -c 'ls -v \"Equipment/Target_Camera/Variables/start_stop\"'"));
         extraction = atoi(grab_odb("odbedit -c 'ls -v \"Equipment/Target_Camera/Variables/start_stop\"'"));

         if( ODB_start_stop == 0) {
            sleep(1);
            if (j==cycle_time/2) printf("half way done");
         }
         
         if(ODB_start_stop==1){
            ODB_start_stop =0;
            system("odbedit -c 'set \"Equipment/Target_Camera/Variables/start_stop\" 0'");
            initiate_while=1;
            button = 0;
            FILE *f = fopen("/home/meg/online/web/mhttpd/camerasettings.txt", "w");
            fprintf(f, "%f,%d,%d,%d,%d,%d", exposure_time, num_photos, cycle_time, led_intensity, light,button);
            fclose(f);
            FILE *out8 = fopen("/home/meg/online/web/mhttpd/readout.txt", "a");
            myTxt[0] = 0;
            strcpy(myTxt, "");
            sprintf(myTxt, "Stop timed cycle command received:%d", (int)time(NULL));
            strcat(myTxt, "\n");
            fprintf(out8, "%s", myTxt);
            fclose(out8);
            break;
         }
      }
      
//--sleeps indefinitely until start_stop ODB value is set to start, then immediately begins another run
//  skipped if full sleep time is elapsed

//--loop will search for start/value until it is told to start, then it will break the loop
      while (initiate_while ==1) { 
         ODB_start_stop = atoi(grab_odb("odbedit -c 'ls -v \"Equipment/Target_Camera/Variables/start_stop\"'"));
         printf("cycle searching for ODB start");
         if( ODB_start_stop == 0)
            sleep(1);
         if (ODB_start_stop == 1) {
            printf(" broke the while loop");
            ODB_start_stop =0;
            FILE *out9 = fopen("/home/meg/online/web/mhttpd/readout.txt", "a");
            myTxt[0] = 0;
            strcpy(myTxt, "");
            sprintf(myTxt, "Start command for new image sequence recieved, readout will clear and restart:%d", (int)time(NULL));
            strcat(myTxt, "\n");
            fprintf(out9, "%s", myTxt);
            fclose(out9);
            system("odbedit -c 'set \"Equipment/Target_Camera/Variables/start_stop\" 0'");
            break;
         }
      }
      
   }
}


   //strcpy(analysis_error, buffer_dell);
   //system(("odbedit -c 'set \"Equipment/Target_Camera/Settings/analysis_error\" %s'", analysis_error));
   
   //nbytes_dell = ssh_channel_read(channel_dell, buffer_dell, sizeof(buffer_dell), 0); // reading analysis output
   //while (nbytes_dell > 0) {
   // fwrite(buffer_dell, 1, nbytes_dell, stdout);
   //   nbytes_dell = ssh_channel_read(channel_dell, buffer_dell, sizeof(buffer_dell), 0);
   //}
   //free_channel(channel_dell); //disconnecting from dell
   //free_session(session_dell);
   //return 1;  //need to delete eventually
#define _BSD_SOURCE
