# Project Overview

This project consists of two main Python scripts that interact with each other to control a pan-tilt mechanism. The scripts communicate by passing data through a `config.txt` file, using locks to ensure safe data exchange.

## Files

### 1. pantilt2.py

This script is responsible for:
- Controlling the pan-tilt mechanism based on the instructions read from the `config.txt` file.
- Ensuring smooth and precise movements of the pan-tilt system.

### 2. pantiltmessager.py

This script handles:
- Sending messages or commands to the `pantilt2.py` script by writing to the `config.txt` file.
- Using locks to ensure that data written to `config.txt` is not corrupted and is read correctly by `pantilt2.py`.

## Data Exchange

- The `config.txt` file is used for communication between the scripts.
- Locks are implemented to ensure safe and synchronized data exchange, preventing race conditions and ensuring that the data remains consistent.

## Usage

1. **Setup**: Ensure that both scripts are in the same directory and that the `config.txt` file is present.
2. **Running**:
   - Start the `pantilt2.py` script to initialize the pan-tilt mechanism.
   - Use the `pantiltmessager.py` script to send commands or messages.
3. **Communication**: The `pantiltmessager.py` script will write commands to `config.txt`, and `pantilt2.py` will read and execute these commands, maintaining synchronization with the help of locks.

## Dependencies

- Ensure that you have all the necessary libraries and modules installed to run these scripts. You might need to install additional packages based on your specific setup and hardware requirements.

## Note

- Proper error handling and logging are recommended to track the performance and identify any issues during the operation of the scripts.

---

This README provides a brief overview of the project's functionality and how to use the provided scripts effectively. For more detailed information, refer to the comments and documentation within the scripts.
