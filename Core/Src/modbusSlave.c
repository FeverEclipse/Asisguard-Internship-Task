/*!
  ******************************************************************************
  * @file           : modbusSlave.c
  * @brief          : Modbus slave functionality.
  ******************************************************************************
 */

#include "modbusSlave.h"
#include "main.h"
#include "modbus_crc.h"
#include "string.h"
#include "tmpsensor.h"
#include "system_stm32g4xx.h"

extern uint8_t rx_buffer[256];
extern uint8_t tx_buffer[256];
extern UART_HandleTypeDef huart2;
extern uint16_t calculatedCrc;
extern uint16_t receivedCrc;
extern TIM_HandleTypeDef htim3;
uint64_t desiredTimesSystemCore;
uint32_t arr;
double timeS;

/*! \brief This function sets the timer 3's frequency(in milliseconds).
 *
 */
uint8_t setFrequency()
{
	receivedCrc = (rx_buffer[6]<<8|rx_buffer[7]);
	uint8_t crcList[6];
	for(int i= 0; i < 6 ; i++){
		crcList[i] = rx_buffer[i];
	}
	calculatedCrc = crc16(crcList, sizeof(crcList));
	if(!(calculatedCrc == receivedCrc)){
		return 0;
	}


	timeS = ((rx_buffer[2]<<24)|(rx_buffer[3]<<16)|(rx_buffer[4]<<8)|(rx_buffer[5]));
	desiredTimesSystemCore = (uint64_t) (SystemCoreClock * timeS) / 1000;
	uint32_t PSC = 0;
	while((desiredTimesSystemCore / (PSC + 1)) > 0xFFFF || desiredTimesSystemCore % (PSC + 1) != 0){ /* Max number that can be represented with 32 bits */
		PSC++;
	}
	arr = (desiredTimesSystemCore / (PSC + 1)) - 1;
	htim3.Instance->ARR = arr;
	htim3.Instance->PSC = PSC;
	TIM3->CCR2 = arr / 2;
	return 1;
}
