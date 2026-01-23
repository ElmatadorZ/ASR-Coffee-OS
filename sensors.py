class SensorInput:
    def __init__(self):
        self.data = {}

    def ingest_artisan_log(self, log: dict):
        self.data["artisan"] = log

    def ingest_ble_temp(self, temp_c: float):
        self.data["slurry_temp"] = temp_c

    def ingest_refractometer(self, tds: float):
        self.data["tds"] = tds

    def validate(self) -> bool:
        return len(self.data) > 0
