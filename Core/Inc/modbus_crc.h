/*
 * modbus_crc.h
 *
 *  Created on: Sep 16, 2022
 *      Author: arunr
 */
#include "main.h"

#ifndef INC_MODBUS_CRC_H_
#define INC_MODBUS_CRC_H_

uint16_t crc16(uint8_t *buffer, uint16_t buffer_length);


#endif /* INC_MODBUS_CRC_H_ */
