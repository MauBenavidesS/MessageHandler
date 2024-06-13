"""
This module provides functions to handle the generation and parsing of request and response messages for communication with a device. 
The `generate_request_message` function creates a request message byte string based on the input command number, ensuring it fits within 
the specified format and length constraints. The `parse_din_status_response` function extracts the status of each contact from a response 
message byte string representing the DIN status. Additionally, the `din_status_to_32bit_signed_integer` function converts the DIN status 
array to a 32-bit signed integer, considering the sign bit and ensuring the value falls within the range of a 32-bit signed integer. 

These functions enable seamless interaction with the device while adhering to the specified communication protocol.
"""

def generate_request_message(command_number: int):
    """
    This function generates a request message byte string according to the specified format, given a command number. 
    It first converts the message ID 'RQ' to a single integer, then ensures the command number fits within 8 bits and 
    raises an exception if it exceeds 32 bits. Next, it extracts the least significant 8 bits of the command number using 
    a bitwise AND operation and combines it with the message ID integer. The checksum is calculated by summing up the bits 
    of the previous bytes, and finally, the message is joined into a single byte string. 
    
    The resulting byte string represents the request message.
    """
    # Bytes 0 to 1, Message ID
    message_id = b'RQ'

    # Convert message_id to a single integer
    int_message_id = int.from_bytes(message_id, byteorder='big')

    # Convert the command number to binary and ensures it is at least an 8-bit number
    bin_command_number = bin(command_number)[2:].zfill(8)

    # Raises exception if the command number is bigger than a 32-bit number 
    num_bits = len(bin_command_number)
    if num_bits > 32:
        raise ValueError("Command number should be less or equal to 32 bits long.")
    
    # Byte 2, Bitwise AND operation with the bitmask 0xFF to extract the least significant 8 bits of the command number which can be a 32-bit signed integer
    command_number_8bit = command_number & 0xFF

    # Combine the message_id integer and the command_number
    int_rep_0to2_bytes = (int_message_id << 8) | command_number_8bit
    bin_rep_0to2_bytes = bin(int_rep_0to2_bytes)[2:].zfill(24)

    # Byte 3, Calculate the Checksum of previous bytes
    int_rep_3rd_byte = int(bin_rep_0to2_bytes[0:8], 2) + int(bin_rep_0to2_bytes[8:16], 2)+ int(bin_rep_0to2_bytes[16:24], 2)

    # Join Bytes 0 through 3 into a single message
    int_rep_0to3_bytes = (int_rep_0to2_bytes << 8) | int_rep_3rd_byte
    bin_rep_0to3_bytes = bin(int_rep_0to3_bytes)[2:].zfill(32)

    return bin_rep_0to3_bytes

def parse_din_status_response(response_message: str):
    """
    This function parses a DIN status response message byte string to extract the status of each contact. It determines the byte length 
    of the DIN status field using the 3rd byte of the message. Then, it stores the DIN status as a binary string and converts it into an 
    array where each contact status is represented as an integer value. 
    
    The resulting array contains the status of each contact.
    """
    # Uses the 3rd byte to confirm the byte length of the data field (DIN status).
    byte_lenght_of_din_status = int(response_message[24:40], 2)
    
    # Stores the DIN status as a binary string
    starting_index_of_din_status = 40
    din_status = response_message[starting_index_of_din_status : (starting_index_of_din_status + byte_lenght_of_din_status * 8)]
    
    # Stores the DIN status in an array, each contact is stored as an int value
    array_din_status = list(int(contact) for contact in din_status)

    return array_din_status

def din_status_to_32bit_signed_integer(response_message: list[int]):
    """
    This function converts a DIN status array into a 32-bit signed integer. It ensures the array length is less than or equal to 32 bits, 
    raising an exception otherwise. Then, it combines the bits into a bit string and converts it to an unsigned integer. If the sign bit 
    is set, indicating a negative value, it calculates the signed value by subtracting 2^num_bits. Finally, it ensures the value falls 
    within the range of a 32-bit signed integer by masking it with 0xFFFFFFFF and adjusting it if necessary. 
    
    The resulting integer represents the DIN status data field as a 32-bit signed integer.
    """

    # Ensure the array length less than 32 bits long
    if len(response_message) > 32:
        raise ValueError("Array length must be a less or equal than 32 bits long.")
    
    # Combine the bits into a bit string
    bit_string = ''.join(str(bit) for bit in response_message)
    
    # Convert the bit string to an unsigned integer
    unsigned_value = int(bit_string, 2)
    
    # Determine the number of bits
    num_bits = len(response_message)

    # Check if the number should be negative (if the sign bit is set)
    if unsigned_value & (1 << (num_bits - 1)):
        # Calculate the signed value by subtracting 2^num_bits
        signed_value = unsigned_value - (1 << num_bits)
    else:
        signed_value = unsigned_value
    
    # Ensure the value is within the 32-bit signed integer range
    signed_value_32bit = signed_value & 0xFFFFFFFF
    if signed_value_32bit >= 0x80000000:
        signed_value_32bit -= 0x100000000

    return signed_value_32bit

# Example usage
cmd_num = 0x1F
request_message = generate_request_message(command_number=cmd_num)
print("Request Message:", request_message, type(request_message))

message = '01010010010100110001111100000000000000011010101011111111'
parsed_status = parse_din_status_response(response_message=message)
print("Parsed Status:", parsed_status)

array = [1,0,1,0,1,0,0,1,1,0,0,0,1,0,1,0,1,0,1,0,0,1,1,0,0,0,1,0,1,0,1,1]
data_field_int = din_status_to_32bit_signed_integer(response_message=array)
print("Data Field as Integer:", data_field_int)
