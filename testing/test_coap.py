# pylint: disable=invalid-name, missing-class-docstring, missing-function-docstring

import os
import json
import pytest
from pyairctrl.coap_client import CoAPAirClient
from pyairctrl.airctrl import CoAPCli
from coap_test_server import CoAPTestServer
from coap_resources import SyncResource, ControlResource, StatusResource


class TestCoap:
    @pytest.fixture(scope="class")
    def air_client(self):
        return CoAPAirClient("127.0.0.1")

    @pytest.fixture(scope="class")
    def air_cli(self):
        return CoAPCli("127.0.0.1")

    @pytest.fixture(scope="class")
    def test_data(self):
        return self._test_data()

    def _test_data(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "data.json"), "r") as json_file:
            return json.load(json_file)

    @pytest.fixture(scope="class")
    def sync_resource(self):
        return SyncResource()

    @pytest.fixture(scope="class")
    def status_resource(self):
        return StatusResource()

    @pytest.fixture(scope="class")
    def control_resource(self):
        return ControlResource()

    @pytest.fixture(autouse=True)
    def set_defaults(self, control_resource, status_resource):
        control_resource.append_data('{"mode": "A"}')
        status_resource.set_dataset("coap-status")

    @pytest.fixture(scope="class", autouse=True)
    def coap_server(self, sync_resource, status_resource, control_resource):
        server = CoAPTestServer(5683)
        server.add_url_rule("/sys/dev/status", status_resource)
        server.add_url_rule("/sys/dev/control", control_resource)
        server.add_url_rule("/sys/dev/sync", sync_resource)
        server.start()
        yield server
        server.stop()

    # def test_set_values(self, air_client):
    #     values = {}
    #     values["mode"] = "A"
    #     result = air_client.set_values(values)
    #     assert result

    def test_get_status_is_valid(
        self, sync_resource, status_resource, air_client, test_data
    ):
        self.assert_json_data(
            air_client.get_status,
            "coap-status",
            test_data,
            air_client,
            sync_resource,
            status_resource,
        )

    def test_get_firmware_is_valid(
        self, sync_resource, status_resource, air_client, test_data
    ):
        self.assert_json_data(
            air_client.get_firmware,
            "coap-status",
            test_data,
            air_client,
            sync_resource,
            status_resource,
        )

    def test_get_filters_is_valid(
        self, sync_resource, status_resource, air_client, test_data
    ):
        self.assert_json_data(
            air_client.get_filters,
            "coap-status",
            test_data,
            air_client,
            sync_resource,
            status_resource,
        )

    def test_get_cli_status_is_valid(
        self, sync_resource, status_resource, air_cli, test_data, capfd
    ):
        self.assert_cli_data(
            air_cli.get_status,
            "coap-status-cli",
            test_data,
            air_cli,
            capfd,
            sync_resource,
            status_resource,
        )

    def test_get_cli_status_err193_is_valid(
        self, sync_resource, status_resource, air_cli, test_data, capfd
    ):
        dataset = "coap-status-err193"
        status_resource.set_dataset(dataset)
        self.assert_cli_data(
            air_cli.get_status,
            "{}-cli".format(dataset),
            test_data,
            air_cli,
            capfd,
            sync_resource,
            status_resource,
        )

    def test_get_cli_firmware_is_valid(
        self, sync_resource, status_resource, air_cli, test_data, capfd
    ):
        self.assert_cli_data(
            air_cli.get_firmware,
            "coap-firmware-cli",
            test_data,
            air_cli,
            capfd,
            sync_resource,
            status_resource,
        )

    def test_get_cli_filters_is_valid(
        self, sync_resource, status_resource, air_cli, test_data, capfd
    ):
        self.assert_cli_data(
            air_cli.get_filters,
            "coap-fltsts-cli",
            test_data,
            air_cli,
            capfd,
            sync_resource,
            status_resource,
        )

    def assert_json_data(
        self, air_func, dataset, test_data, air_client, sync_resource, status_resource
    ):
        status_resource.set_encryption_key(sync_resource.encryption_key)

        result = air_func()
        data = test_data[dataset]["data"]
        json_data = json.loads(data)
        assert result == json_data

    def assert_cli_data(
        self,
        air_func,
        dataset,
        test_data,
        air_cli,
        capfd,
        sync_resource,
        status_resource,
    ):
        status_resource.set_encryption_key(sync_resource.encryption_key)

        air_func()
        result, err = capfd.readouterr()
        assert result == test_data[dataset]["data"]
