import scrapy

class NpcSpider(scrapy.Spider):
    name = "npc"
    def get_url(self):
        return f"https://game.eoserv.net/npc?npc={self.npc_id}"

    def start_requests(self):
        self.npc_id = 1
        self.drops = []
        self.shops = []

        yield scrapy.Request(url=self.get_url(), callback=self.parse)

    def parse(self, response):
        drops = self.get_drops(response)
        crafts = self.get_crafts(response)
        trades = self.get_trades(response)

        if crafts != '' or trades != '':
            name = response.css("th::text").re('\(([^)]+)\)')[0]
            self.shops.append(f"{self.npc_id}.name = {name}")
            if trades != '':
                self.shops.append(trades)
            if crafts != '':
                self.shops.append(crafts)

        if drops != '':
            self.drops.append(drops)

        print(self.drops)
        print(self.shops)

        if len(response.css("h2::text").getall()) == 1:
            self.write_files()
        else:
            self.npc_id += 1
            yield scrapy.Request(self.get_url(), callback=self.parse)

    def get_drops(self, response):
        rows = response.css('#npc-drops tbody tr')
        if len(rows) == 0:
            return ''

        drops = f"{self.npc_id} = "
        index = 0
        for row in rows:
            item = get_item_id(row.css('a::attr(href)').get())
            amount = row.css('td::text')[0].get().split('-')
            _min = amount[0].strip()
            if len(amount) > 1:
                _max = amount[1].strip()
            else:
                _max = _min
            rate = row.css('td::text')[1].get()
            rate = rate[0:rate.index('%')]
            if index > 0:
                drops += ', '
            drops += f"{item},{_min},{_max},{rate}"
            index += 1

        return drops

    def get_crafts(self, response):
        rows = response.css('#npc-craft tbody tr')
        if len(rows) == 0:
            return ''

        crafts = f"{self.npc_id}.craft = "
        index = 0
        for row in rows:
            items = row.css('a::attr(href)').getall()
            item = get_item_id(items[0])
            amounts = row.css('td::text').re('[0-9]+')
            if index > 0:
                crafts += ', '

            crafts += f"{item},"

            for item_index in range(1,5):
                if item_index > 1:
                    crafts += ','
                if len(items) > item_index:
                    ingredient = get_item_id(items[item_index])
                    amount = amounts[item_index - 1]
                    crafts += f"{ingredient},{amount}"
                else:
                    crafts += '0,0'

            index += 1

        return crafts

    def get_trades(self, response):
        rows = response.css('#npc-shop tbody tr')
        if len(rows) == 0:
            return ''

        trades = f"{self.npc_id}.trades = "
        index = 0
        for row in rows:
            item = get_item_id(row.css('a::attr(href)').get())
            types = row.css('b::text').getall()
            prices = row.css('td::text').re('[0-9]+')
            buy = '0'
            sell = '0'
            if len(prices) == 1 and types[0] == 'Sell:':
                buy = '0'
                sell = prices[0].strip().replace(',', '')
            elif len(prices) == 1 and types[0] == 'Buy:':
                buy = prices[0].strip().replace(',', '')
                sell = '0'
            else:
                buy = prices[0].strip().replace(',', '')
                sell = prices[1].strip().replace(',', '')

            if index > 0:
                trades += ', '
            trades += f"{item},{buy},{sell}"
            index += 1

        return trades

    def write_files(self):
        if len(self.drops) > 0:
            with open("drops.ini", "wt") as f:
                f.write('\n'.join(self.drops))
        if len(self.shops) > 0:
            with open("shops.ini", "wt") as f:
                f.write('\n'.join(self.shops))

def get_item_id(url):
    return url.split('=')[1]
