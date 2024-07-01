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
extern uint64_t desiredTimesSystemCore;
extern uint32_t arr;
extern double timeS;

/*!
 *  \brief This function takes in the data buffer and adds the CRC bytes to it. And then transmits the data to the master device.
 *  \param *data Data buffer without the CRC bytes added.
 *  \param size The size of the data buffer before adding the CRC bytes.
*/
void sendData (uint8_t *data, int size)
{
	// we will calculate the CRC in this function itself
	uint16_t crc = crc16(data, size);
	data[size] = (crc>>8)&0xFF;   // CRC LOW
	data[size+1] = crc&0xFF;  // CRC HIGH
	HAL_UART_Transmit(&huart2, data, size+2, 1000);
}

/*!
 *  \brief This function creates an exception message and passes it to the sendData function.
 *
 *  The byte structure of the response is as follows:\n
 *  | SLAVE_ID -> 1 BYTE | FUNCTION_CODE -> 1 BYTE | Exception code -> 1 BYTE | CRC -> 2 BYTES |\n
 *  \param exceptioncode The exception code to add to the transmit buffer.
*/
void modbusException (uint8_t exceptioncode)
{
	tx_buffer[0] = rx_buffer[0];       // slave ID
	tx_buffer[1] = rx_buffer[1]|0x80;  // adding 1 to the MSB of the function code
	tx_buffer[2] = exceptioncode;   // Load the Exception code
	sendData(tx_buffer, 3);         // send Data... CRC will be calculated in the function
}

/*!
 * \brief This function adds the requested holding registers from the received message to the transmit buffer and passes it to the sendData function.
 *
 * The holding registers are read-write permitted for outside-of-device access and can be used for temporary/custom values.
 * The byte structure of the response is as follows:\n
 * | SLAVE_ID -> 1 BYTE | FUNCTION_CODE -> 1 BYTE | BYTE COUNT -> 1 BYTE | DATA -> N(Requested register count)*2 BYTES| CRC -> 2 BYTES|
 */
uint8_t readHoldingRegs (void)
{
	uint16_t startAddr = ((rx_buffer[2]<<8)|rx_buffer[3]);  // start Register Address

	uint16_t numRegs = ((rx_buffer[4]<<8)|rx_buffer[5]);   // number to registers master has requested
	if ((numRegs<1)||(numRegs>50))  // maximum no. of Registers as per the PDF
	{
		modbusException (ILLEGAL_DATA_VALUE);  // send an exception
		return 0;
	}

	uint16_t endAddr = startAddr+numRegs-1;  // end Register
	if (endAddr>49)  // end Register can not be more than 49 as we only have record of 50 Registers in total
	{
		modbusException(ILLEGAL_DATA_ADDRESS);   // send an exception
		return 0;
	}

	receivedCrc = (rx_buffer[6]<<8|rx_buffer[7]);
	uint8_t crcList[6];
	for(int i= 0; i < 6 ; i++){
		crcList[i] = rx_buffer[i];
	}
	calculatedCrc = crc16(crcList, sizeof(crcList));
	if(!(calculatedCrc == receivedCrc)){
		modbusException(ILLEGAL_CRC);
		return 0;
	}

	// Prepare TxData buffer

	//| SLAVE_ID | FUNCTION_CODE | BYTE COUNT | DATA      | CRC     |
	//| 1 BYTE   |  1 BYTE       |  1 BYTE    | N*2 BYTES | 2 BYTES |

	tx_buffer[0] = SLAVE_ID;  // slave ID
	tx_buffer[1] = rx_buffer[1];  // function code
	tx_buffer[2] = numRegs*2;  // Byte count
	int indx = 3;  // we need to keep track of how many bytes has been stored in TxData Buffer

	for (int i=0; i<numRegs; i++)   // Load the actual data into TxData buffer
	{
		tx_buffer[indx++] = (Holding_Registers_Database[startAddr]>>8)&0xFF;  // extract the higher byte
		tx_buffer[indx++] = (Holding_Registers_Database[startAddr])&0xFF;   // extract the lower byte
		startAddr++;  // increment the register address
	}

	sendData(tx_buffer, indx);  // send data... CRC will be calculated in the function itself
	return 1;   // success
}
/*!
 *  \brief This function updates the input values in the Input_Registers_Database list.
 *
 *  Only the temperature sensor value is used currently.
*/
uint8_t updateInputs(void)
{
	if (Flg.ADCCMPLT){
		Adc.IntSensTmp = TMPSENSOR_getTemperature(Adc.Raw[1], Adc.Raw[0]);
		Flg.ADCCMPLT = 0; /* Nullify flag */
	}
	Input_Registers_Database[0] = Adc.IntSensTmp;
	return 1;
}

/*!
 * \brief This function adds the requested input registers from the received message to the transmit buffer and passes it to the sendData function.
 *
 * The input registers are read-only for outside-of-device access and used for storing sensor related information.
 * The byte structure of the response is as follows:\n
 * | SLAVE_ID -> 1 BYTE | FUNCTION_CODE -> 1 BYTE | BYTE COUNT -> 1 BYTE | DATA -> N(Requested register count)*2 BYTES| CRC -> 2 BYTES|
 */
uint8_t readInputRegs (void)
{
	updateInputs(); // Update inputs database

	uint16_t startAddr = ((rx_buffer[2]<<8)|rx_buffer[3]);  // start Register Address

	uint16_t numRegs = ((rx_buffer[4]<<8)|rx_buffer[5]);   // number to registers master has requested
	if ((numRegs<1)||(numRegs>50))  // maximum no. of Registers as per the protocol
	{
		modbusException(ILLEGAL_DATA_VALUE);  // send an exception
		return 0;
	}

	uint16_t endAddr = startAddr+numRegs-1;  // end Register
	if (endAddr>49)  // end Register can not be more than 49 as we only have record of 50 Registers in total
	{
		modbusException(ILLEGAL_DATA_ADDRESS);   // send an exception
		return 0;
	}

	receivedCrc = (rx_buffer[6]<<8|rx_buffer[7]);
	uint8_t crcList[6];
	for(int i= 0; i < 6 ; i++){
		crcList[i] = rx_buffer[i];
	}
	calculatedCrc = crc16(crcList, sizeof(crcList));
	if(!(calculatedCrc == receivedCrc)){
		modbusException(ILLEGAL_CRC);
		return 0;
	}

	// Prepare TxData buffer

	//| SLAVE_ID | FUNCTION_CODE | BYTE COUNT | DATA      | CRC     |
	//| 1 BYTE   |  1 BYTE       |  1 BYTE    | N*2 BYTES | 2 BYTES |

	tx_buffer[0] = SLAVE_ID;  // slave ID
	tx_buffer[1] = rx_buffer[1];  // function code
	tx_buffer[2] = numRegs*2;  // Byte count
	int indx = 3;  // we need to keep track of how many bytes has been stored in TxData Buffer

	for (int i=0; i<numRegs; i++)   // Load the actual data into TxData buffer
	{
		tx_buffer[indx++] = (Input_Registers_Database[startAddr]>>8)&0xFF;  // extract the higher byte
		tx_buffer[indx++] = (Input_Registers_Database[startAddr])&0xFF;   // extract the lower byte
		startAddr++;  // increment the register address
	}

	sendData(tx_buffer, indx);  // send data... CRC will be calculated in the function itself
	return 1;   // success
}
/*!
 * \brief This function writes to a single register specified by the request message.
 *
 * The byte structure of the response is as follows:\n
 * | SLAVE_ID -> 1 BYTE | FUNCTION_CODE -> 1 BYTE | Start Addr -> 2 BYTES | Data -> 2 BYTES | CRC -> 2 BYTES |
 */
uint8_t writeSingleReg (void)
{
	uint16_t startAddr = ((rx_buffer[2]<<8)|rx_buffer[3]);  // start Register Address

	if (startAddr>49)  // The Register Address can not be more than 49 as we only have record of 50 Registers in total
	{
		modbusException(ILLEGAL_DATA_ADDRESS);   // send an exception
		return 0;
	}

	receivedCrc = (rx_buffer[6]<<8|rx_buffer[7]);
	uint8_t crcList[6];
	for(int i= 0; i < 6 ; i++){
		crcList[i] = rx_buffer[i];
	}
	calculatedCrc = crc16(crcList, sizeof(crcList));
	if(!(calculatedCrc == receivedCrc)){
		modbusException(ILLEGAL_CRC);
		return 0;
	}
	/* Save the 16 bit data
	 * Data is the combination of 2 bytes, RxData[4] and RxData[5]
	 */

	Holding_Registers_Database[startAddr] = (rx_buffer[4]<<8)|rx_buffer[5];

	// Prepare Response

	//| SLAVE_ID | FUNCTION_CODE | Start Addr | Data     | CRC     |
	//| 1 BYTE   |  1 BYTE       |  2 BYTE    | 2 BYTES  | 2 BYTES |

	tx_buffer[0] = SLAVE_ID;    // slave ID
	tx_buffer[1] = rx_buffer[1];   // function code
	tx_buffer[2] = rx_buffer[2];   // Start Addr HIGH Byte
	tx_buffer[3] = rx_buffer[3];   // Start Addr LOW Byte
	tx_buffer[4] = rx_buffer[4];   // Reg Data HIGH Byte
	tx_buffer[5] = rx_buffer[5];   // Reg Data LOW  Byte

	sendData(tx_buffer, 6);  // send data... CRC will be calculated in the function itself
	return 1;   // success
}

/*!
 *  \brief This function increments a specified register by one and passes it to the sendData function.
 *
 *  \details The byte structure of the response is as follows:\n
 *	| Slave ID -> 1 BYTE | Function Code -> 1 BYTE | Register Address -> 2 BYTES | Updated Register Value -> 2 BYTES | CRC -> 2 BYTES|
 *
*/
uint8_t incrementRegByOne(void){
	uint16_t startAddr = ((rx_buffer[2]<<8)|rx_buffer[3]);

	if (startAddr>49)  // The Register Address can not be more than 49 as we only have record of 50 Registers in total
		{
			modbusException(ILLEGAL_DATA_ADDRESS);   // send an exception
			return 0;
		}

	receivedCrc = (rx_buffer[4]<<8|rx_buffer[5]);
	uint8_t crcList[4];
	for(int i= 0; i < 4 ; i++){
		crcList[i] = rx_buffer[i];
	}
	calculatedCrc = crc16(crcList, sizeof(crcList));
	if(!(calculatedCrc == receivedCrc)){
		modbusException(ILLEGAL_CRC);
		return 0;
	}

	Holding_Registers_Database[startAddr]++;
	if(Holding_Registers_Database[startAddr] > 256){
		Holding_Registers_Database[startAddr]=0;
	}
	tx_buffer[0] = SLAVE_ID;    // slave ID
	tx_buffer[1] = rx_buffer[1];   // function code
	tx_buffer[2] = rx_buffer[2];   // Start Addr HIGH Byte
	tx_buffer[3] = rx_buffer[3];   // Start Addr LOW Byte
	tx_buffer[4] = (Holding_Registers_Database[startAddr]>>8)&0xFF;
	tx_buffer[5] = Holding_Registers_Database[startAddr]&0xFF;

	sendData(tx_buffer, 6);
	return 1;
}
/*!
 *  \brief This function decrements a specified register by one and passes it to the sendData function.
 *
 *  \details The byte structure of the response is as follows:\n
    | Slave ID -> 1 BYTE | Function Code -> 1 BYTE | Register Address -> 2 BYTES | Updated Register Value -> 2 BYTES | CRC -> 2 BYTES |
 *
*/
uint8_t decrementRegByOne(void){
	uint16_t startAddr = ((rx_buffer[2]<<8)|rx_buffer[3]);

	if (startAddr>49)  // The Register Address can not be more than 49 as we only have record of 50 Registers in total
		{
			modbusException(ILLEGAL_DATA_ADDRESS);   // send an exception
			return 0;
		}

	receivedCrc = (rx_buffer[4]<<8|rx_buffer[5]);
	uint8_t crcList[4];
	for(int i= 0; i < 4 ; i++){
		crcList[i] = rx_buffer[i];
	}
	calculatedCrc = crc16(crcList, sizeof(crcList));
	if(!(calculatedCrc == receivedCrc)){
		modbusException(ILLEGAL_CRC);
		return 0;
	}
	Holding_Registers_Database[startAddr]--;
	if(Holding_Registers_Database[startAddr] < 2){
		Holding_Registers_Database[startAddr] = 512;
	}
	tx_buffer[0] = SLAVE_ID;    // slave ID
	tx_buffer[1] = rx_buffer[1];   // function code
	tx_buffer[2] = rx_buffer[2];   // Start Addr HIGH Byte
	tx_buffer[3] = rx_buffer[3];   // Start Addr LOW Byte
	tx_buffer[4] = (Holding_Registers_Database[startAddr]>>8)&0xFF;
	tx_buffer[5] = Holding_Registers_Database[startAddr]&0xFF;

	sendData(tx_buffer, 6);
	return 1;
}
/*!
 * \deprecated
 * \brief This function adds the temperature value from the device to the buffer and passes it to the sendData function.
 *
 * The first element of the Input_Registers_Database list is assigned to the temperature value
 * and it is advised to use readInputRegisters function for retrieving the temperature data from the device.
 * This is made to obey the default Modbus function code instead of this custom function.
 *
 * The byte structure of the response is as follows:\n
 * | Slave ID -> 1 BYTE | Function Code -> 1 BYTE | Temperature Value -> 1 BYTE | CRC -> 2 BYTES |
 * \param temp The temperature value from the sensor.
 */
uint8_t readTemp(double temp){
	receivedCrc = (rx_buffer[2]<<8|rx_buffer[3]);
		uint8_t crcList[2];
		for(int i= 0; i < 2 ; i++){
			crcList[i] = rx_buffer[i];
		}
		calculatedCrc = crc16(crcList, sizeof(crcList));
		if(!(calculatedCrc == receivedCrc)){
			modbusException(ILLEGAL_CRC);
			return 0;
		}

	tx_buffer[0] = SLAVE_ID; // Slave ID
	tx_buffer[1] = rx_buffer[1]; // Function code (0x0A)
	tx_buffer[2] = (uint8_t) temp; // Set the temperature value to send.
	sendData(tx_buffer, 3);
	return 1;
}

