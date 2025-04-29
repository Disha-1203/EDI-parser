import json
import re


def read_orders_from_txt(filename):
    with open(filename, 'r') as file:
        content = file.read()

    raw_orders = re.split(r'\n\s*\n', content.strip())

    orders = []
    for raw in raw_orders:
        order = {}
        for line in raw.strip().split('\n'):
            if ':' in line:
                key, value = line.strip().split(':', 1)
                order[key.strip()] = value.strip()
        if order:
            orders.append(order)

    return orders


def read_orders_from_json(filename):
    with open(filename, 'r') as file:
        orders = json.load(file)
    return orders


def read_orders_from_edi(filename):
    with open(filename, 'r') as f:
        content = f.read()

    blocks = content.split('ISA')
    orders = []
    for block in blocks:
        if block.strip():
            edi_order = 'ISA' + block.strip()
            # very basic EDI parsing: extract simple fields
            po_number = re.search(r'BEG\*00\*NE\*(.*?)\*', edi_order)
            order_date = re.search(r'DTM\*\d+\*(\d+)', edi_order)
            item = re.search(r'PO1\*\d+\*\d+\*EA\*\d+\.\d+\*\w+\*VN\*(.*?)\n', edi_order)
            quantity = re.search(r'PO1\*\d+\*(\d+)\*', edi_order)
            unit_price = re.search(r'PO1\*\d+\*\d+\*EA\*(\d+\.\d+)\*', edi_order)

            order = {}
            if po_number:
                order['PO_Number'] = po_number.group(1)
            if order_date:
                order['Order_Date'] = order_date.group(1)
            if item:
                order['Item'] = item.group(1)
            if quantity:
                order['Quantity'] = quantity.group(1)
            if unit_price:
                order['Unit_Price'] = unit_price.group(1)

            if order:
                orders.append(order)
    return orders


def convert_to_json(orders, json_file):
    with open(json_file, 'w') as file:
        json.dump(orders, file, indent=2)
    print(f" Converted to {json_file}")


def convert_to_txt(orders, txt_file):
    with open(txt_file, 'w') as file:
        for order in orders:
            for key, value in order.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")
    print(f" Converted to {txt_file}")


def convert_to_edi(orders, edi_file):
    with open(edi_file, 'w') as file:
        for order in orders:
            file.write("ISA*00*          *00*          *ZZ*AMAZON         *12*9622309900     *      *    *U*00401*000000001*0*T*>\n")
            file.write("GS*PO*AMAZON*9622309900*20240424*1056**X*004010\n")
            file.write("ST*850*0001\n")
            file.write(f"BEG*00*NE*{order['PO_Number']}*4783291*{order['Order_Date']}\n")
            file.write(f"DTM*064*{order['Order_Date']}\n")
            file.write(f"PO1*1*{order['Quantity']}*EA*{order['Unit_Price']}*PE*VN*{order['Item']}\n")
            file.write("CTT*1*5\n")
            file.write("SE*12*0001\n")
            file.write("GE*1*1\n")
            file.write("IEA*1*000000001\n")
            file.write("\n")
    print(f" Converted to {edi_file}")


def main():
    print(" Welcome to EDI/TXT/JSON Parser Program ")
    
    mode_input = input(" Choose mode: (1 for Single Order, 2 for Multiple Orders): ").strip()
    mode = "single" if mode_input == "1" else "multiple" if mode_input == "2" else None

    file_name = input(" Enter input file name (with extension): ").strip()

    # Detect file type based on extension
    if file_name.lower().endswith('.txt'):
        orders = read_orders_from_txt(file_name)
    elif file_name.lower().endswith('.json'):
        orders = read_orders_from_json(file_name)
    elif file_name.lower().endswith('.edi'):
        orders = read_orders_from_edi(file_name)
    else:
        print(" Unsupported file type!")
        return

    print(f" Total orders found: {len(orders)}")

    if mode == "multiple":
        filter_date = input(" Do you want to filter by date range? (yes/no): ").lower()
        
        if filter_date == 'yes':
            start_date = input(" Enter start date (YYYYMMDD): ").strip()
            end_date = input(" Enter end date (YYYYMMDD): ").strip()

            filtered_orders = [order for order in orders if start_date <= order['Order_Date'] <= end_date]
            print(f" Total orders after filtering: {len(filtered_orders)}")
        else:
            filtered_orders = orders

        output_format = input(" Choose output format: (txt/json/edi): ").lower()

        if output_format == 'txt':
            convert_to_txt(filtered_orders, 'output.txt')
        elif output_format == 'json':
            convert_to_json(filtered_orders, 'output.json')
        elif output_format == 'edi':
            convert_to_edi(filtered_orders, 'output.edi')
        else:
            print(" Invalid format selected.")
    
    elif mode == "single":
        print(" Available orders:")
        for i, order in enumerate(orders, 1):
            print(f"{i}. PO Number: {order.get('PO_Number', 'N/A')}, Order Date: {order.get('Order_Date', 'N/A')}")

        order_indices = input(" Enter order indices to process (comma-separated, e.g. 1,3,4): ")
        selected_indices = [int(index.strip()) - 1 for index in order_indices.split(',')]

        selected_orders = []
        for index in selected_indices:
            if 0 <= index < len(orders):
                selected_orders.append(orders[index])
            else:
                print(f" Invalid index: {index + 1}")

        if selected_orders:
            output_format = input(" Choose output format: (txt/json/edi): ").lower()

            if output_format == 'txt':
                convert_to_txt(selected_orders, 'output_single.txt')
            elif output_format == 'json':
                convert_to_json(selected_orders, 'output_single.json')
            elif output_format == 'edi':
                convert_to_edi(selected_orders, 'output_single.edi')
            else:
                print(" Invalid format selected.")
        else:
            print(" No valid orders selected.")
    else:
        print(" Invalid mode selected.")


if __name__ == "__main__":
    main()
