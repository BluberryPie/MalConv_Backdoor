import struct


def fill_dos_header(data, pattern):

    # Compute PE Header Offset
    pe_header_offset = struct.unpack('<l', data[0x3C:0x40])[0]

    # Fill DOS Header
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
