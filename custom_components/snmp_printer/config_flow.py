"""Config flow for SNMP Printer."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .const import (
    CONF_AUTH_KEY,
    CONF_AUTH_PROTOCOL,
    CONF_COMMUNITY,
    CONF_PRIV_KEY,
    CONF_PRIV_PROTOCOL,
    CONF_SNMP_VERSION,
    CONF_UPDATE_INTERVAL,
    DEFAULT_COMMUNITY,
    DEFAULT_PORT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .snmp_client import SNMPClient

_LOGGER = logging.getLogger(__name__)


class SNMPPrinterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SNMP Printer."""

    VERSION = 1
    _discovered_hosts: set[str] = (
        set()
    )  # Class variable for cross-instance deduplication

    def __init__(self):
        """Initialize the config flow."""
        self.discovery_info = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        return await self.async_step_manual()

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual printer configuration."""
        errors = {}

        if user_input is not None:
            # Create SNMP client and test connection
            client = SNMPClient(
                host=user_input[CONF_HOST],
                port=user_input.get(CONF_PORT, DEFAULT_PORT),
                snmp_version=user_input.get(CONF_SNMP_VERSION, "2c"),
                community=user_input.get(CONF_COMMUNITY, DEFAULT_COMMUNITY),
                username=user_input.get(CONF_USERNAME),
                auth_protocol=user_input.get(CONF_AUTH_PROTOCOL),
                auth_key=user_input.get(CONF_AUTH_KEY),
                priv_protocol=user_input.get(CONF_PRIV_PROTOCOL),
                priv_key=user_input.get(CONF_PRIV_KEY),
            )

            try:
                # Get printer info to verify connection
                system_info = await client.get_system_info()
                device_info = await client.get_device_info()

                # Use serial number as unique ID, fallback to host
                unique_id = device_info.get("serial_number", user_input[CONF_HOST])

                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                # Extract model name from description for better title
                description = system_info.get("description") or ""
                location = system_info.get("location") or ""
                name = system_info.get("name") or ""

                # Try to get model name from description PID field
                model_name = None
                if description and "PID:" in description:
                    parts = description.split("PID:")
                    if len(parts) > 1:
                        model_name = parts[1].split(",")[0].split(";")[0].strip()
                elif location:
                    model_name = location
                elif name:
                    model_name = name

                # Create entry with printer model as title
                title = model_name or user_input[CONF_HOST]

                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input.get(CONF_PORT, DEFAULT_PORT),
                        CONF_SNMP_VERSION: user_input.get(CONF_SNMP_VERSION, "2c"),
                        CONF_COMMUNITY: user_input.get(
                            CONF_COMMUNITY, DEFAULT_COMMUNITY
                        ),
                        CONF_USERNAME: user_input.get(CONF_USERNAME),
                        CONF_AUTH_PROTOCOL: user_input.get(CONF_AUTH_PROTOCOL),
                        CONF_AUTH_KEY: user_input.get(CONF_AUTH_KEY),
                        CONF_PRIV_PROTOCOL: user_input.get(CONF_PRIV_PROTOCOL),
                        CONF_PRIV_KEY: user_input.get(CONF_PRIV_KEY),
                        CONF_UPDATE_INTERVAL: user_input.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    },
                )

            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Error connecting to printer")
                errors["base"] = "cannot_connect"

        # Determine SNMP version (from user_input or default)
        snmp_version = user_input.get(CONF_SNMP_VERSION, "2c") if user_input else "2c"

        # Build schema based on SNMP version
        if snmp_version == "3":
            # SNMPv3 - show username and authentication options
            data_schema = vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=user_input.get(CONF_HOST, "") if user_input else "",
                    ): str,
                    vol.Optional(
                        CONF_PORT,
                        default=(
                            user_input.get(CONF_PORT, DEFAULT_PORT)
                            if user_input
                            else DEFAULT_PORT
                        ),
                    ): int,
                    vol.Required(CONF_SNMP_VERSION, default="3"): vol.In(
                        ["1", "2c", "3"]
                    ),
                    vol.Required(
                        CONF_USERNAME,
                        default=user_input.get(CONF_USERNAME, "") if user_input else "",
                    ): str,
                    vol.Optional(
                        CONF_AUTH_PROTOCOL,
                        default=(
                            user_input.get(CONF_AUTH_PROTOCOL) if user_input else None
                        ),
                    ): vol.In(["MD5", "SHA", "SHA224", "SHA256", "SHA384", "SHA512"]),
                    vol.Optional(
                        CONF_AUTH_KEY,
                        default=user_input.get(CONF_AUTH_KEY, "") if user_input else "",
                    ): str,
                    vol.Optional(
                        CONF_PRIV_PROTOCOL,
                        default=(
                            user_input.get(CONF_PRIV_PROTOCOL) if user_input else None
                        ),
                    ): vol.In(["DES", "3DES", "AES", "AES192", "AES256"]),
                    vol.Optional(
                        CONF_PRIV_KEY,
                        default=user_input.get(CONF_PRIV_KEY, "") if user_input else "",
                    ): str,
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=(
                            user_input.get(
                                CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                            )
                            if user_input
                            else DEFAULT_UPDATE_INTERVAL
                        ),
                    ): int,
                }
            )
        else:
            # SNMPv1/v2c - show community string
            data_schema = vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=user_input.get(CONF_HOST, "") if user_input else "",
                    ): str,
                    vol.Optional(
                        CONF_PORT,
                        default=(
                            user_input.get(CONF_PORT, DEFAULT_PORT)
                            if user_input
                            else DEFAULT_PORT
                        ),
                    ): int,
                    vol.Optional(CONF_SNMP_VERSION, default=snmp_version): vol.In(
                        ["1", "2c", "3"]
                    ),
                    vol.Optional(
                        CONF_COMMUNITY,
                        default=(
                            user_input.get(CONF_COMMUNITY, DEFAULT_COMMUNITY)
                            if user_input
                            else DEFAULT_COMMUNITY
                        ),
                    ): str,
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=(
                            user_input.get(
                                CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                            )
                            if user_input
                            else DEFAULT_UPDATE_INTERVAL
                        ),
                    ): int,
                }
            )

        return self.async_show_form(
            step_id="manual",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        # Extract host from discovery info
        host = discovery_info.host

        if not host:
            return self.async_abort(reason="unknown")

        # Check if we already processed this IP in this session (class variable)
        if host in SNMPPrinterConfigFlow._discovered_hosts:
            _LOGGER.debug(
                "Already processed discovery for %s, skipping duplicate", host
            )
            return self.async_abort(reason="already_in_progress")

        # Mark this IP as being processed (class variable)
        SNMPPrinterConfigFlow._discovered_hosts.add(host)

        # Try to get printer info to set unique ID and get model name
        # Try v2c first, then fall back to v1 if that fails
        system_info = None
        device_info = None
        working_version = None

        for snmp_version in ["2c", "1"]:
            try:
                _LOGGER.info(
                    "Trying to connect to %s using SNMP v%s", host, snmp_version
                )
                client = SNMPClient(
                    host=host,
                    port=DEFAULT_PORT,
                    snmp_version=snmp_version,
                    community=DEFAULT_COMMUNITY,
                    timeout=2.5,  # 2.5 seconds per request
                    retries=1,  # 1 retry = total ~5 seconds max per version
                )
                system_info = await client.get_system_info()
                device_info = await client.get_device_info()

                # Check if we actually got useful data (not all None)
                has_data = (
                    system_info.get("description")
                    or system_info.get("name")
                    or device_info.get("serial_number")
                    or device_info.get("mac_address")
                )

                if has_data:
                    working_version = snmp_version
                    _LOGGER.info(
                        "Successfully connected to %s using SNMP v%s",
                        host,
                        snmp_version,
                    )
                    break  # Success, exit the loop
                else:
                    _LOGGER.warning(
                        "SNMP v%s connected to %s but returned no data, trying next version",
                        snmp_version,
                        host,
                    )
                    system_info = None
                    device_info = None
                    continue

            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning(
                    "Could not connect to %s using SNMP v%s: %s",
                    host,
                    snmp_version,
                    err,
                )
                import traceback

                _LOGGER.debug("Traceback: %s", traceback.format_exc())
                continue  # Try next version

        # If we couldn't connect with either version, abort
        if system_info is None or device_info is None:
            _LOGGER.warning(
                "Could not connect to discovered device at %s with any SNMP version",
                host,
            )
            SNMPPrinterConfigFlow._discovered_hosts.discard(
                host
            )  # Remove from set so it can be retried
            return self.async_abort(reason="not_printer")

        try:
            # Log what we got from SNMP
            _LOGGER.debug("System info from %s: %s", host, system_info)
            _LOGGER.debug("Device info from %s: %s", host, device_info)

            # Extract manufacturer and model from description (same logic as sensor.py)
            description = system_info.get("description") or ""
            location = system_info.get("location") or ""
            name = system_info.get("name") or ""

            # Try to get model name from description PID field
            model = "Unknown Printer"
            if description and "PID:" in description:
                parts = description.split("PID:")
                if len(parts) > 1:
                    model = parts[1].split(",")[0].split(";")[0].strip()
            elif location:
                model = location
            elif name:
                model = name

            # Extract manufacturer
            manufacturer = "Unknown"
            if description:
                if "HP" in description or "Hewlett-Packard" in description:
                    manufacturer = "HP"
                elif "Canon" in description:
                    manufacturer = "Canon"
                elif "Epson" in description:
                    manufacturer = "Epson"
                elif "Brother" in description:
                    manufacturer = "Brother"
                elif "Lexmark" in description:
                    manufacturer = "Lexmark"
                elif "Samsung" in description:
                    manufacturer = "Samsung"
                elif "Xerox" in description:
                    manufacturer = "Xerox"

            # Get serial number for unique ID
            unique_id = device_info.get("serial_number")

            if not unique_id:
                # If no serial number, use MAC address or host as fallback
                unique_id = device_info.get("mac_address", host)

            # Set unique ID based on serial number to prevent duplicate discoveries
            await self.async_set_unique_id(unique_id)
            # Update the host if IP changed, but don't abort - let user see it
            self._abort_if_unique_id_configured(updates={CONF_HOST: host})

            _LOGGER.info(
                "Discovered printer: %s %s at %s (unique_id: %s)",
                manufacturer,
                model,
                host,
                unique_id,
            )

            # Set the title in the context so it appears in the discovery card
            self.context["title_placeholders"] = {
                "name": model,
                "model": model,
                "manufacturer": manufacturer,
            }

            # Store discovery info with actual printer model name
            self.discovery_info = {
                CONF_HOST: host,
                "name": model,
                "model": model,
                "manufacturer": manufacturer,
                "snmp_version": working_version,  # Store the working version
            }

            # If we got here, it's a valid printer
            return await self.async_step_zeroconf_confirm()

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("Error processing discovered device at %s: %s", host, err)
            import traceback

            _LOGGER.debug("Traceback: %s", traceback.format_exc())
            SNMPPrinterConfigFlow._discovered_hosts.discard(
                host
            )  # Remove from set so it can be retried
            return self.async_abort(reason="not_printer")

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        if user_input is not None:
            # User confirmed, proceed to manual setup with pre-filled data from discovery
            return await self.async_step_manual(
                {
                    CONF_HOST: self.discovery_info[CONF_HOST],
                    CONF_SNMP_VERSION: self.discovery_info.get("snmp_version", "2c"),
                    CONF_PORT: DEFAULT_PORT,
                    CONF_COMMUNITY: DEFAULT_COMMUNITY,
                    CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL,
                }
            )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={
                "name": self.discovery_info.get("name", "Unknown Printer"),
                "model": self.discovery_info.get("model", "Unknown"),
                "manufacturer": self.discovery_info.get("manufacturer", "Unknown"),
                "host": self.discovery_info[CONF_HOST],
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for SNMP Printer."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        super().__init__()
        self._data = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - first step with connection settings."""
        errors = {}

        if user_input is not None:
            # Store the connection settings
            self._data.update(user_input)

            # If SNMP version changed to v3, go to auth step
            if user_input.get(CONF_SNMP_VERSION) == "3":
                return await self.async_step_auth()

            # Otherwise, go to final step to test and save
            return await self.async_step_complete()

        # Build schema for connection settings
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=self.config_entry.data.get(CONF_HOST),
                ): str,
                vol.Optional(
                    CONF_PORT,
                    default=self.config_entry.data.get(CONF_PORT, DEFAULT_PORT),
                ): int,
                vol.Required(
                    CONF_SNMP_VERSION,
                    default=self.config_entry.data.get(CONF_SNMP_VERSION, "2c"),
                ): vol.In(["1", "2c", "3"]),
                vol.Optional(
                    CONF_COMMUNITY,
                    default=self.config_entry.data.get(
                        CONF_COMMUNITY, DEFAULT_COMMUNITY
                    ),
                ): str,
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_UPDATE_INTERVAL,
                        self.config_entry.data.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ),
                ): int,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_auth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure SNMPv3 authentication."""
        if user_input is not None:
            # Store auth settings
            self._data.update(user_input)
            return await self.async_step_complete()

        # Build schema for SNMPv3 authentication
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_USERNAME,
                    default=self.config_entry.data.get(CONF_USERNAME, ""),
                ): str,
                vol.Optional(
                    CONF_AUTH_PROTOCOL,
                    default=self.config_entry.data.get(CONF_AUTH_PROTOCOL),
                ): vol.In(["MD5", "SHA", "SHA224", "SHA256", "SHA384", "SHA512"]),
                vol.Optional(
                    CONF_AUTH_KEY,
                    default=self.config_entry.data.get(CONF_AUTH_KEY, ""),
                ): str,
                vol.Optional(
                    CONF_PRIV_PROTOCOL,
                    default=self.config_entry.data.get(CONF_PRIV_PROTOCOL),
                ): vol.In(["DES", "3DES", "AES", "AES192", "AES256"]),
                vol.Optional(
                    CONF_PRIV_KEY,
                    default=self.config_entry.data.get(CONF_PRIV_KEY, ""),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="auth",
            data_schema=data_schema,
        )

    async def async_step_complete(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Test connection and save settings."""
        errors = {}

        # Build full config from stored data
        snmp_version = self._data.get(CONF_SNMP_VERSION)

        # Create client with new settings
        client = SNMPClient(
            host=self._data.get(CONF_HOST),
            port=self._data.get(CONF_PORT, DEFAULT_PORT),
            snmp_version=snmp_version,
            community=(
                self._data.get(CONF_COMMUNITY, DEFAULT_COMMUNITY)
                if snmp_version != "3"
                else None
            ),
            username=self._data.get(CONF_USERNAME) if snmp_version == "3" else None,
            auth_protocol=(
                self._data.get(CONF_AUTH_PROTOCOL) if snmp_version == "3" else None
            ),
            auth_key=self._data.get(CONF_AUTH_KEY) if snmp_version == "3" else None,
            priv_protocol=(
                self._data.get(CONF_PRIV_PROTOCOL) if snmp_version == "3" else None
            ),
            priv_key=self._data.get(CONF_PRIV_KEY) if snmp_version == "3" else None,
        )

        try:
            await client.get_system_info()

            # Update the config entry data (not just options)
            # This updates the actual configuration
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=self._data,
            )

            # Also store in options for consistency
            return self.async_create_entry(title="", data=self._data)

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Error connecting to printer with new settings")
            errors["base"] = "cannot_connect"

            # Go back to init step
            self._data = {}
            return await self.async_step_init(user_input={})
