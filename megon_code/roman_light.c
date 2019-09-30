#include <libssh/libssh.h>
#include <stdlib.h>
#include <stdio.h>

void free_channel(ssh_channel channel) {
    ssh_channel_send_eof(channel);
    ssh_channel_close(channel);
    ssh_channel_free(channel);
}

void free_session(ssh_session session) {
    ssh_disconnect(session);
    ssh_free(session);
}


void error(ssh_session session) {
    fprintf(stderr, "Error: %s\n", ssh_get_error(session));
    free_session(session);
    exit(-1);
}

int ssh_to_pi(char* hostname, char* user, char* password, char* led_command) {
  
    ssh_session session;
    ssh_channel channel;
    int rc, port = 22;
    char buffer[1024] = "";
    unsigned int nbytes;


    printf("Session...\n");
    session = ssh_new();
    if (session == NULL) exit(-1);

    ssh_options_set(session, SSH_OPTIONS_HOST, hostname);
    ssh_options_set(session, SSH_OPTIONS_PORT, &port);
    ssh_options_set(session, SSH_OPTIONS_USER, user);

    printf("Connecting...\n");
    rc = ssh_connect(session);
    if (rc != SSH_OK) error(session);

    printf("Password Autentication...\n");
    rc = ssh_userauth_password(session, NULL, password);
    if (rc != SSH_AUTH_SUCCESS) error(session);

    printf("Channel...\n");
    channel = ssh_channel_new(session);
    if (channel == NULL) exit(-1);

    printf("Opening...\n");
    rc = ssh_channel_open_session(channel);
    if (rc != SSH_OK) error(session);

    channel = ssh_channel_new(session);
    rc = ssh_channel_open_session(channel);
    int nbytes_test = 0;
    char buffer_test[1024]= "";

    printf("Executing remote command...\n");
    rc = ssh_channel_request_exec(channel, led_command);
    if (rc != SSH_OK) error(session);

    printf("Readout: \n");
    nbytes_test = ssh_channel_read(channel, buffer_test, sizeof(buffer_test), 0);
    //printf("number of bytes %d ", nbytes);
    //nbytes= 0;
    while (nbytes_test > 0) {
        fwrite(buffer_test, 1, nbytes_test, stdout);
        nbytes_test = ssh_channel_read(channel, buffer_test, sizeof(buffer_test), 0);
    }

    free_channel(channel);
    free_session(session);
    return 0;
}

int main(int argc, char **argv)
{
  int light_number, ontime, intensity;
  char led_command[100];
  ontime = 10; //seconds
  intensity = 5; // 1-10 integer value
  sprintf(led_command, "python3 roman_lights.py %i %i", ontime, intensity);

  ssh_to_pi("UCItgtRPI", "pi", "muegamma", led_command); //ip has to be changed once it is moved to PSI
}
 
