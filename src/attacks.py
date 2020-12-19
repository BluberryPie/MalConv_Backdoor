import struct


def fill_dos_header(data, pattern, partial=False):

    # Compute PE Header Offset
    pe_header_offset = struct.unpack('<l', data[0x3C:0x40])[0]

    # Fill DOS Header
    if partial:
        dos_header_slack_len = (0x3C - 0x2)
        filler = pattern * (dos_header_slack_len // len(pattern) + 1)
        filler = filler[:dos_header_slack_len]
        data[0x2:0x3C] = filler

    # Fill Slack Space Between DOS Header and PE Header
    intermediate_slack_len = (pe_header_offset - 0x40)
    filler = pattern * (intermediate_slack_len // len(pattern) + 1)
    filler = filler[:intermediate_slack_len]
    data[0x40:pe_header_offset] = filler

    return data


def dos_header_extension(data, pattern, extend_len):

    def patch_section_header(rear_data):
        
        # Compute Section Table Offset
        optional_header_len = struct.unpack('<h', rear_data[0x14:0x16])[0]
        section_header_offset = 0x18 + optional_header_len

        # Add Extension Length to Pointers
        num_sections = struct.unpack('<h', rear_data[0x06:0x08])[0]

        for i in range(num_sections):
            offset = section_header_offset + 0x28 * i
            original_ptr = struct.unpack('<l', rear_data[offset + 0x14 : offset + 0x18])[0]

            rear_data[offset + 0x14:offset + 0x18] = struct.pack(
                '<l', original_ptr + extend_len
            )

        return rear_data

    # Compute PE Header Offset
    pe_header_offset = struct.unpack('<l', data[0x3C:0x40])[0]

    # Shift PE Header Offset
    data[0x3C:0x40] = struct.pack('<l', pe_header_offset + extend_len)

    # Fill Trigger Pattern in Between
    filler = pattern * (extend_len // len(pattern) + 1)
    filler = filler[:extend_len]
    data = data[:pe_header_offset] + filler + patch_section_header(data[pe_header_offset:])

    return data


def padding_append(data, pattern, length):

    padding = pattern * (length // len(pattern) + 1)
    padding = padding[:length]
    data += padding

    return data
