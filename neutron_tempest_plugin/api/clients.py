# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest import clients as tempest_clients
from tempest.lib.services import clients
from tempest.lib.services.compute import availability_zone_client
from tempest.lib.services.compute import hypervisor_client
from tempest.lib.services.compute import interfaces_client
from tempest.lib.services.compute import keypairs_client
from tempest.lib.services.compute import servers_client
from tempest.lib.services.identity.v2 import tenants_client
from tempest.lib.services.identity.v3 import projects_client
from tempest.lib.services.network import qos_limit_bandwidth_rules_client
from tempest.lib.services.network import qos_minimum_bandwidth_rules_client
from tempest.lib.services.network import qos_minimum_packet_rate_rules_client

from neutron_tempest_plugin import config
from neutron_tempest_plugin.services.network.json import network_client

CONF = config.CONF


class Manager(clients.ServiceClients):
    """Top level manager for OpenStack tempest clients"""
    default_params = {
        'disable_ssl_certificate_validation':
            CONF.identity.disable_ssl_certificate_validation,
        'ca_certs': CONF.identity.ca_certificates_file,
        'trace_requests': CONF.debug.trace_requests,
        'proxy_url': CONF.service_clients.proxy_url
    }

    # NOTE: Tempest uses timeout values of compute API if project specific
    # timeout values don't exist.
    default_params_with_timeout_values = {
        'build_interval': CONF.compute.build_interval,
        'build_timeout': CONF.compute.build_timeout
    }
    default_params_with_timeout_values.update(default_params)

    def __init__(self, credentials=None, service=None):
        dscv = CONF.identity.disable_ssl_certificate_validation
        _, uri = tempest_clients.get_auth_provider_class(credentials)
        super(Manager, self).__init__(
            credentials=credentials,
            identity_uri=uri,
            scope='project',
            disable_ssl_certificate_validation=dscv,
            ca_certs=CONF.identity.ca_certificates_file,
            trace_requests=CONF.debug.trace_requests)

        self._set_identity_clients()

        self.network_client = network_client.NetworkClientJSON(
            self.auth_provider,
            CONF.network.catalog_type,
            CONF.network.region or CONF.identity.region,
            endpoint_type=CONF.network.endpoint_type,
            build_interval=CONF.network.build_interval,
            build_timeout=CONF.network.build_timeout,
            **self.default_params)

        params = {
            'service': CONF.compute.catalog_type,
            'region': CONF.compute.region or CONF.identity.region,
            'endpoint_type': CONF.compute.endpoint_type,
            'build_interval': CONF.compute.build_interval,
            'build_timeout': CONF.compute.build_timeout
        }
        params.update(self.default_params)

        self.servers_client = servers_client.ServersClient(
            self.auth_provider,
            enable_instance_password=CONF.compute_feature_enabled
                .enable_instance_password,
            **params)
        self.interfaces_client = interfaces_client.InterfacesClient(
            self.auth_provider, **params)
        self.keypairs_client = keypairs_client.KeyPairsClient(
            self.auth_provider, **params)
        self.hv_client = hypervisor_client.HypervisorClient(
            self.auth_provider, **params)
        self.az_client = availability_zone_client.AvailabilityZoneClient(
            self.auth_provider, **params)

        self.qos_limit_bandwidth_rules_client = \
            qos_limit_bandwidth_rules_client.QosLimitBandwidthRulesClient(
                self.auth_provider,
                CONF.network.catalog_type,
                CONF.network.region or CONF.identity.region,
                endpoint_type=CONF.network.endpoint_type,
                build_interval=CONF.network.build_interval,
                build_timeout=CONF.network.build_timeout,
                **self.default_params)

        self.qos_minimum_bandwidth_rules_client = \
            qos_minimum_bandwidth_rules_client.QosMinimumBandwidthRulesClient(
                self.auth_provider,
                CONF.network.catalog_type,
                CONF.network.region or CONF.identity.region,
                endpoint_type=CONF.network.endpoint_type,
                build_interval=CONF.network.build_interval,
                build_timeout=CONF.network.build_timeout,
                **self.default_params)

        self.qos_minimum_packet_rate_rules_client = \
            qos_minimum_packet_rate_rules_client.\
            QosMinimumPacketRateRulesClient(
                self.auth_provider,
                CONF.network.catalog_type,
                CONF.network.region or CONF.identity.region,
                endpoint_type=CONF.network.endpoint_type,
                build_interval=CONF.network.build_interval,
                build_timeout=CONF.network.build_timeout,
                **self.default_params)

    def _set_identity_clients(self):
        params = {
            'service': CONF.identity.catalog_type,
            'region': CONF.identity.region
        }
        params.update(self.default_params_with_timeout_values)
        params_v2_admin = params.copy()
        params_v2_admin['endpoint_type'] = CONF.identity.v2_admin_endpoint_type
        # Client uses admin endpoint type of Keystone API v2
        self.tenants_client = tenants_client.TenantsClient(self.auth_provider,
                                                           **params_v2_admin)
        # Client uses admin endpoint type of Keystone API v3
        self.projects_client = projects_client.ProjectsClient(
            self.auth_provider, **params_v2_admin)
