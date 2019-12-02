import sys
import xmltodict

MAGIC = b"\x00\xe9\x55\x43\x4c\xff\x01\x1a"

if len(sys.argv) != 2 or ".xml." not in sys.argv[1]:
    print("Please give xml file to use")
    sys.exit(1)

XML_FILE = sys.argv[1]

BIN_FILE = XML_FILE.replace(".xml.", ".bin.")


def build_header(decompression_method=b"\x2b", level=b"\x01"):
    """
    Flags: Mostly unclear, LSByte controls the generation of a CRC-32 (different from the one in your xml file
    decompression_method: 2B, 2D, 2E are available, only 2B works with your file.
    level: 1-10?

    Block Size: Memory for the decompressor. Must have at least the size of the uncompressed block.
    xxd block_size
    00000000: 0002 0000                                ....

    Uncompressed Size: As read from your xml file
    xxd decomp_size
    00000000: 0002 0000                                ....


    Compressed Size:As read from your xml file.
    xxd comp_size
    00000000: 0001 83d6


    """
    header = b""

    header += MAGIC
    flags = b"\x00\x00\x00\x00"
    header += flags

    header += decompression_method

    header += level

    source_size_string, target_size_string = parse_xml()
    print("compressed size:", source_size_string)
    print("decompressed size:", target_size_string)

    compressed_size = source_size_string.to_bytes(4, byteorder='big')
    decompressed_size = target_size_string.to_bytes(4, byteorder='big')

    # block size - need to know unpacked size first, or default to something giant
    # example was 0002 0000 which is 128KB
    # block_size = b"\x00\x02\x00\x00"
    # block_size = b"\x00\x08\x00\x00" # should be 1/2MB
    block_size = decompressed_size
    header += block_size

    header += decompressed_size

    header += compressed_size

    return header


def parse_xml():
    with open(XML_FILE) as input_file:
        doc = xmltodict.parse(input_file.read())

    flash_segment = doc['BINARY-HEADER']['BINARY-FLASHBLOCK']['FLASH-SEGMENTS']['FLASH-SEGMENT']

    source_start = flash_segment['SOURCE-START-ADDRESS']
    source_end = flash_segment['SOURCE-END-ADDRESS']
    source_size = int(source_end, 16) - int(source_start, 16) + 1

    target_start = flash_segment['TARGET-START-ADDRESS']
    target_end = flash_segment['TARGET-END-ADDRESS']
    target_size = int(target_end, 16) - int(target_start, 16) + 1

    return source_size, target_size


header = build_header()

UCL_BIN_FILE = BIN_FILE+'.ucl'
with open(UCL_BIN_FILE, 'wb') as output_file:
    output_file.write(header)
    with open(BIN_FILE, 'rb') as packed_bin:
        output_file.write(packed_bin.read())

print("Created new file with UCL header attached - "+UCL_BIN_FILE)
print("Try to unpack it now")
print("Even if it errors it might have unpacked most/all of it")
print("  docker-compose run ucl -d "+UCL_BIN_FILE+" "+BIN_FILE+".unpacked")
