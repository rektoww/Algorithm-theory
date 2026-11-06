import httpx


class SleepTrackerAPI:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def _request(self, method, path, data=None):
        response = httpx.request(
            method,
            f"{self.base_url}{path}",
            json=data,
            timeout=3.0,
        )

        response.raise_for_status()

        if response.status_code == 204:
            return None

        return response.json()

    def get_records(self):
        return self._request("GET", "/records")

    def get_record(self, record_id):
        return self._request(
            "GET",
            f"/records/{record_id}"
        )

    def create_record(self, data):
        return self._request(
            "POST",
            "/records",
            data
        )

    def update_record(self, record_id, data):
        return self._request(
            "PUT",
            f"/records/{record_id}",
            data
        )

    def delete_record(self, record_id):
        return self._request(
            "DELETE",
            f"/records/{record_id}"
        )

    def get_statistics(self):
        return self._request("GET", "/statistics")

    def get_activity_log(self):
        return self._request("GET", "/activity-log")