import xml.etree.ElementTree as ET
import socks
import socket
import logging
from concurrent.futures import ThreadPoolExecutor

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def check_socks5_proxy(proxy_data):
    host, port, username, password = proxy_data
    s = socks.socksocket()
    try:
        if username and password:
            s.set_proxy(socks.SOCKS5, host, int(port), username=username, password=password)
        else:
            s.set_proxy(socks.SOCKS5, host, int(port))
        s.settimeout(10)
        s.connect(("1.1.1.1", 80))
        s.close()
        return True, host, port, username, password
    except Exception as e:
        return False, host, port, username, password
    finally:
        s.close()


def parse_proxy_line(proxy_line):
    parts = proxy_line.split('@')
    user_info, address_info = parts[0].split('://')[1], parts[1]
    username, password = user_info.split(':')
    address, port = address_info.split(':')
    return address, port, username, password


def fill_template_with_proxies(template_path, proxies_path, output_path):
    tree = ET.parse(template_path)
    root = tree.getroot()
    proxy_list = root.find("ProxyList")
    rule_list = root.find("RuleList")

    with open(proxies_path, 'r') as f:
        proxies = [parse_proxy_line(line.strip()) for line in f.readlines()]

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(check_socks5_proxy, proxy) for proxy in proxies]
        for future in futures:
            success, host, port, username, password = future.result()
            if success:
                logger.info(f"Прокси {host}:{port} успешно прошел проверку.")
                proxy_id = len(proxy_list) + 1000
                proxy_element = create_proxy_element(proxy_id, username, password, host, port)
                proxy_list.append(proxy_element)

                app_name = f"Telegram{proxy_id-999}.exe"
                rule_element = create_rule_element(proxy_id, app_name)
                rule_list.append(rule_element)
            else:
                logger.warning(f"Прокси {host}:{port} не доступен.")

    xml_str = ET.tostring(root, encoding="unicode")
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        output_file.write(xml_str)


def create_proxy_element(proxy_id, username, password, address, port):
    proxy = ET.Element("Proxy", id=str(proxy_id), type="SOCKS5")
    auth = ET.SubElement(proxy, "Authentication", enabled="true")
    ET.SubElement(auth, "Username").text = username
    ET.SubElement(auth, "Password").text = password
    ET.SubElement(proxy, "Address").text = address
    ET.SubElement(proxy, "Port").text = port
    return proxy


def create_rule_element(proxy_id, app_name):
    rule = ET.Element("Rule", enabled="true")
    ET.SubElement(rule, "Action", type="Proxy").text = str(proxy_id)
    ET.SubElement(rule, "Applications").text = app_name
    ET.SubElement(rule, "Name").text = app_name
    return rule


def main():
    template_path = "./template.ppx"
    proxies_path = "./proxy.txt"
    output_path = "./proxy_profile.ppx"
    fill_template_with_proxies(template_path, proxies_path, output_path)


if __name__ == '__main__':
    main()
