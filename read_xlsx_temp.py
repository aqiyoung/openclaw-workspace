#!/usr/bin/env python3
import zipfile, xml.etree.ElementTree as ET

xlsx_path = '/vol1/1000/报告/2026年6月工作总结.xlsx'

with zipfile.ZipFile(xlsx_path, 'r') as z:
    print('=== Files in xlsx ===')
    for name in z.namelist():
        print(name)
    print()
    
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_xml = z.read('xl/sharedStrings.xml')
        root = ET.fromstring(ss_xml)
        ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for si in root.findall('.//ns:si', ns):
            texts = []
            for t in si.findall('.//ns:t', ns):
                if t.text:
                    texts.append(t.text)
            shared_strings.append(''.join(texts))
        print(f'=== Shared Strings ({len(shared_strings)}) ===')
        for i, s in enumerate(shared_strings):
            print(f'  [{i}] {s}')
    else:
        print('No sharedStrings.xml found')
    
    print()
    
    sheet_xml = z.read('xl/worksheets/sheet1.xml')
    root = ET.fromstring(sheet_xml)
    ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    dim = root.find('.//ns:dimension', ns)
    if dim is not None:
        print(f'Sheet dimension: {dim.get("ref")}')
    
    print()
    print('=== Sheet1 Data ===')
    rows = root.findall('.//ns:sheetData/ns:row', ns)
    for row in rows:
        row_num = row.get('r')
        cells = row.findall('ns:c', ns)
        cell_data = []
        for cell in cells:
            ref = cell.get('r')
            cell_type = cell.get('t', '')
            value_elem = cell.find('ns:v', ns)
            value = value_elem.text if value_elem is not None else ''
            
            is_elem = cell.find('ns:is', ns)
            if is_elem is not None:
                t_elem = is_elem.find('ns:t', ns)
                if t_elem is not None and t_elem.text:
                    display = t_elem.text
                else:
                    display = value
            elif cell_type == 's' and value:
                idx = int(value)
                display = shared_strings[idx] if idx < len(shared_strings) else f'[MISSING:{value}]'
            else:
                display = value
            
            cell_data.append(f'{ref}={display}')
        
        print(f'Row {row_num}: {" | ".join(cell_data)}')
