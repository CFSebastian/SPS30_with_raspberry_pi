
#include <stdio.h>
#include <string.h>

#include "sensirion_uart.h"
#include "sps30.h"

int main(void) {
    struct sps30_measurement m;
    char serial[SPS30_MAX_SERIAL_LEN];
    const uint8_t AUTO_CLEAN_DAYS = 4;
    int16_t ret;
    char command[128];

    setvbuf(stdout, NULL, _IONBF, 0);

    // Inițializare UART
    while (sensirion_uart_open() != 0) {
        fprintf(stderr, "UART init failed\n");
        sensirion_sleep_usec(1000000);
    }

    // Detectare senzor
    while (sps30_probe() != 0) {
        fprintf(stderr, "SPS30 sensor probing failed\n");
        sensirion_sleep_usec(1000000);
    }
    fprintf(stderr, "SPS30 sensor probing successful\n");

    // Versiune senzor
    struct sps30_version_information version_information;
    ret = sps30_read_version(&version_information);
    if (ret) {
        printf("{\"error\": \"error %d reading version information\"}\n",ret);
        fflush(stdout);
    } else {
        printf("{\"FW\": %u.%u, \"HW\": %u, \"SHDLC\": %u.%u}\n",
        version_information.firmware_major,
        version_information.firmware_minor,
        version_information.hardware_revision,
        version_information.shdlc_major,
        version_information.shdlc_minor);
        fflush(stdout);
    }


    // Serial senzor
    ret = sps30_get_serial(serial);
    if (ret)
        fprintf(stderr, "error %d reading serial\n", ret);

    // Setare curățare automată
    ret = sps30_set_fan_auto_cleaning_interval_days(AUTO_CLEAN_DAYS);
    if (ret)
        fprintf(stderr, "error %d setting auto-clean interval\n", ret);
    
    uint8_t isSleeping = 0;
    // Buclă principală
    while (fgets(command, sizeof(command), stdin)) {
        // Eliminăm newline
        command[strcspn(command, "\n")] = 0;

        if (strcmp(command, "read") == 0) {
            // Pornește măsurare
            if (version_information.firmware_major >= 2 && isSleeping == 1) {
                ret = sps30_wake_up();
                if (ret) {
                    printf("{\"error\": \"Error %i waking up sensor\"}\n",ret);
                    fflush(stdout);
                }
                isSleeping = 0;
            }

            ret = sps30_start_measurement();
            if (ret < 0) {
                printf("{\"error\": \"Start measurement failed\"}\n");
                fflush(stdout);
            }

            // Așteaptă puțin pentru date valide
            sensirion_sleep_usec(5000000);

            ret = sps30_read_measurement(&m);
            if (ret < 0) {
                printf("{\"error\": \"Read measurement failed\"}\n");
                fflush(stdout);
            } else {
                printf("{\"pm1.0\": %.2f, \"pm2.5\": %.2f, \"pm4.0\": %.2f, \"pm10.0\": %.2f, \"nc0.5\": %.2f, \"nc1.0\": %.2f, \"nc2.5\": %.2f, \"nc4.0\": %.2f, \"nc10.0\": %.2f, \"typical\": %.2f}\n",
                    m.mc_1p0, m.mc_2p5, m.mc_4p0, m.mc_10p0,
                    m.nc_0p5, m.nc_1p0, m.nc_2p5, m.nc_4p0, m.nc_10p0,
                    m.typical_particle_size);
                fflush(stdout);
            }
            sensirion_sleep_usec(1000000);

            sps30_stop_measurement();
            if (version_information.firmware_major >= 2) {
                ret = sps30_sleep();
                if(ret) {
                    printf("{\"error\": \"Entering sleep failed\"}\n");
                    fflush(stdout);
                }
                isSleeping = 1;
            }
        } else if (strcmp(command, "exit") == 0) {
            break;
        } else {
            printf("{\"error\": \"Unknown command\"}\n");
            fflush(stdout);
        }
    }

    if (sensirion_uart_close() != 0)
        fprintf(stderr, "failed to close UART\n");
    return 0;
}
