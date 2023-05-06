import concurrent.futures
import requests
from bs4 import BeautifulSoup

with open('card.txt', 'r') as f:
    cards = [line.strip() for line in f]

data = {}
with open('info.txt', 'r') as f:
    for line in f:
        key, value = line.strip().split(' = ')
        data[key] = value

with open('log.txt', 'w') as log_file, concurrent.futures.ThreadPoolExecutor() as executor:
    for i in range(0, len(cards), 1000):
        url_list = []  # create an empty list to hold the URLs
        card_idx = i
        while card_idx < min(i+1000, len(cards)):
            card = cards[card_idx]
            url = f"api"
            url_list.append(url)  # add each URL to the list
            print(f"Sending request to {card}")
            card_idx += 1

        # submit all the requests to the ThreadPoolExecutor
        future_to_url = {executor.submit(requests.get, url): url for url in url_list}

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            card = url.split('=')[1].split('&')[0]
            log_file.write(f"{card}\n")
            log_file.flush()

            try:
                response = future.result()
                soup = BeautifulSoup(response.text, 'html.parser')
                data_status = soup.find('span', class_='badge badge-danger')
                data_preview = soup.find('span', class_='badge badge-dark')

                if data_preview:
                    log_file.write(f"{data_preview.text}\n")
                    log_file.flush()
                else:
                    log_file.write(f"{response.text}\n")
                    log_file.flush()
                    print(response.text)

                # Print result immediately after processing each url
                print('-' * 50)
                print(f"Card => {card}:")
                if data_preview:
                    print(f"Result => {data_status.text} => {data_preview.text}")
                else:
                    print(response.text)
                print('-' * 50)

                # remove the card from the list if it was processed successfully
                cards.remove(card)

            except Exception as e:
                print(f"Exception occurred for {url}: {e}")

        # update cards in data1.txt after all the cards in the current batch have been processed
        with open('card.txt', 'w') as f:
            f.write('\n'.join(cards))
