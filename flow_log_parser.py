import os

#This function parses the protocol numbers file and stores it in a dictionary
def create_protocol_map(protocol_mappings):
    protocol_map = dict()
    try:
        with open(protocol_mappings, 'r') as mappings:
            for mapping in mappings:
                if not mapping.strip(): 
                    continue
                fields = mapping.strip().split(",")

                if len(fields) < 2:
                    print(f"Skipping malformed line for Protocol - Protocol name Mapping: {mapping}")
                    continue
                port_number, name = fields[0].strip(), fields[1].strip().lower()
                protocol_map[port_number] = name

    except FileNotFoundError:
        print(f"Error : protocol numbers file was not found")
        exit(1)
    except Exception as e:
        print(f"Error while reading the protocol numbers file: {e}")
        exit(1)

    return protocol_map


#This function parses the lookup table and stores it in a dictionary
def parse_lookup_table(lookup_file):
    lookup = dict()

    try: 
        with open(lookup_file, 'r') as lookups:
            for mapping in lookups:

                if not mapping.strip(): 
                    continue
                fields = mapping.strip().split(",")

                if len(fields) != 3:  
                    print(f"Skipping malformed line: {mapping}")
                    continue

                dstport, protocol, tag = fields
                dstport = dstport.strip().lower()
                protocol = protocol.strip().lower()

                if lookup.get(dstport, None) is None:
                    lookup[dstport] = dict()
                lookup[dstport][protocol] = tag

    except FileNotFoundError:
        print(f"Error : lookup file was not found")
        exit(1)
    except Exception as e:
        print(f"Error while reading the lookup file: {e}")
        exit(1)

    return lookup



#This function processes logs and matches with the looup table.
def process_logs(logs_file, lookup, protocol_map):
    tag_cnt = dict()
    port_cnt = dict()

    try: 
        with open(logs_file, 'r') as logs:
           
            for log in logs:
                log = log.strip()
                if not log:
                    continue
                
                fields = log.split(" ")

                dstport = fields[6].strip().lower()
                protocol = fields[7].strip().lower()

                if dstport == '-' or protocol == '-':
                    print(f"Skipping log entry: Found '-' in dstport or protocol. {log}")
                    continue

                protocol_name = protocol_map.get(protocol, None)
                if protocol_name is None:
                    print(f"Skipping log entry: Protocol name not found for : {protocol}")
                    continue

                port_protocol_key = (dstport, protocol_name)
                port_cnt[port_protocol_key] = port_cnt.get(port_protocol_key, 0) + 1
            
                if lookup.get(dstport, None) is None or lookup[dstport].get(protocol_name, None) is None:
                    tag_cnt["Untagged"] = tag_cnt.get("Untagged", 0) + 1
                    
                else:
                    tag = lookup[dstport].get(protocol_name)
                    tag_cnt[tag] = tag_cnt.get(tag, 0) + 1
        
    except FileNotFoundError:
        print(f"Error: The flow log file '{logs_file}' was not found.")
        exit(1)
    except Exception as e:
        print(f"Error while reading the flow log file: {e}")
        exit(1)
    
    return tag_cnt, port_cnt



#This function writes the output to a file
def write_output_to_file(tag_cnt, port_cnt, output_file):
    try: 
        with open(output_file, 'w') as op:
            op.write("Tag Counts:\n")
            op.write("\n")
            op.write("Tag, Count:\n")

            for tag, count in tag_cnt.items():
                op.write(f"{tag}, {count}\n")

            op.write("\n")
          
            op.write("Port/Protocol Combination Counts:\n")
            op.write("\n")
            op.write("Port, Protocol, Count\n")
            for (port, protocol), count in port_cnt.items():
                op.write(f"{port}, {protocol}, {count}\n")
    except Exception as e:
        print(f"Error while writing to the output file: {e}")
        exit(1)


#This is the main function to run the program
def main():
    lookup_file = 'lookup_table.csv'  # Lookup table file
    flow_log_file = 'flow_logs.txt'   # logs file
    output_file = 'output.txt'        # Output file
    protocol_numbers_file = "protocol-numbers.csv" #protocol file

    if not os.path.exists(protocol_numbers_file):
        print(f"Error: The lookup file '{protocol_numbers_file}' does not exist.")
        exit(1)

    if not os.path.exists(lookup_file):
        print(f"Error: The lookup file '{lookup_file}' does not exist.")
        exit(1)

    if not os.path.exists(flow_log_file):
        print(f"Error: The flow log file '{flow_log_file}' does not exist.")
        exit(1)

    protocol_map = create_protocol_map(protocol_numbers_file)
  
    lookup_table = parse_lookup_table(lookup_file)
  
    tag_cnt, port_cnt = process_logs(flow_log_file, lookup_table, protocol_map)

    write_output_to_file(tag_cnt, port_cnt, output_file)
    print(f"Output successfully written to '{output_file}'.")


if __name__ == "__main__":
    main()

        