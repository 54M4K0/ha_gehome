import logging
from typing import List

from homeassistant.const import EntityCategory
from homeassistant.helpers.entity import Entity
from gehomesdk import ErdCode, ErdApplianceType, ErdCodeClass

from .base import ApplianceApi
from ..entities import GeErdSensor, GeErdBinarySensor, GeErdButton
from ..entities.laundry.ge_dryer_cycle_button import GeDryerCycleButton


_LOGGER = logging.getLogger(__name__)

class DryerApi(ApplianceApi):
    """API class for dryer objects"""
    APPLIANCE_TYPE = ErdApplianceType.DRYER

    def get_all_entities(self) -> List[Entity]:
        base_entities = super().get_all_entities()

        common_entities = [
            GeErdSensor(self, ErdCode.LAUNDRY_MACHINE_STATE, icon_override="mdi:tumble-dryer", entity_category=EntityCategory.DIAGNOSTIC),
            GeErdSensor(self, ErdCode.LAUNDRY_CYCLE, icon_override="mdi:state-machine"),
            GeErdSensor(self, ErdCode.LAUNDRY_SUB_CYCLE, icon_override="mdi:state-machine"),
            GeErdBinarySensor(self, ErdCode.LAUNDRY_END_OF_CYCLE, icon_on_override="mdi:tumble-dryer", icon_off_override="mdi:tumble-dryer"),
            GeErdSensor(self, ErdCode.LAUNDRY_TIME_REMAINING, suggested_uom="min"),
            GeErdSensor(self, ErdCode.LAUNDRY_DELAY_TIME_REMAINING, suggested_uom="h"),
            GeErdBinarySensor(self, ErdCode.LAUNDRY_DOOR, entity_category=EntityCategory.DIAGNOSTIC),
            GeErdBinarySensor(self, ErdCode.LAUNDRY_REMOTE_STATUS, icon_on_override="mdi:tumble-dryer", icon_off_override="mdi:tumble-dryer", entity_category=EntityCategory.DIAGNOSTIC),
            GeErdBinarySensor(self, ErdCode.LAUNDRY_DRYER_BLOCKED_VENT_FAULT, icon_on_override="mdi:alert-circle", icon_off_override="mdi:alert-circle", entity_category=EntityCategory.DIAGNOSTIC),
        ]

        dryer_entities = self.get_dryer_entities()
        
        dryer_entities.extend(
            self.get_dryer_passthrough_entities(common_entities + dryer_entities)
        )

        # Add the start cycle button
        dryer_entities.append(GeDryerCycleButton(self))

        entities = base_entities + common_entities + dryer_entities
        return entities

    def get_dryer_entities(self):
        dryer_entities = []

        if self.has_erd_code(ErdCode.LAUNDRY_DRYER_DRYNESS_LEVEL):
            dryer_entities.extend([GeErdSensor(self, ErdCode.LAUNDRY_DRYER_DRYNESS_LEVEL, entity_category=EntityCategory.DIAGNOSTIC)])
        if self.has_erd_code(ErdCode.LAUNDRY_DRYER_DRYNESSNEW_LEVEL):
            dryer_entities.extend([GeErdSensor(self, ErdCode.LAUNDRY_DRYER_DRYNESSNEW_LEVEL, entity_category=EntityCategory.DIAGNOSTIC)])
        if self.has_erd_code(ErdCode.LAUNDRY_DRYER_TEMPERATURE_OPTION):
            dryer_entities.extend([GeErdSensor(self, ErdCode.LAUNDRY_DRYER_TEMPERATURE_OPTION, entity_category=EntityCategory.DIAGNOSTIC)])
        if self.has_erd_code(ErdCode.LAUNDRY_DRYER_TEMPERATURENEW_OPTION):
            dryer_entities.extend([GeErdSensor(self, ErdCode.LAUNDRY_DRYER_TEMPERATURENEW_OPTION, entity_category=EntityCategory.DIAGNOSTIC)])
        if self.has_erd_code(ErdCode.LAUNDRY_DRYER_TUMBLE_STATUS):
            dryer_entities.extend([GeErdSensor(self, ErdCode.LAUNDRY_DRYER_TUMBLE_STATUS, entity_category=EntityCategory.DIAGNOSTIC)])
        if self.has_erd_code(ErdCode.LAUNDRY_DRYER_EXTENDED_TUMBLE_OPTION_SELECTION):
            dryer_entities.extend([GeErdSensor(self, ErdCode.LAUNDRY_DRYER_EXTENDED_TUMBLE_OPTION_SELECTION, entity_category=EntityCategory.DIAGNOSTIC)])
        if self.has_erd_code(ErdCode.LAUNDRY_DRYER_WASHERLINK_STATUS):
            dryer_entities.extend([GeErdBinarySensor(self, ErdCode.LAUNDRY_DRYER_WASHERLINK_STATUS, entity_category=EntityCategory.DIAGNOSTIC)])
        if self.has_erd_code(ErdCode.LAUNDRY_DRYER_LEVEL_SENSOR_DISABLED):
            dryer_entities.extend([GeErdBinarySensor(self, ErdCode.LAUNDRY_DRYER_LEVEL_SENSOR_DISABLED, entity_category=EntityCategory.DIAGNOSTIC)])
        if self.has_erd_code(ErdCode.LAUNDRY_DRYER_SHEET_USAGE_CONFIGURATION):
            dryer_entities.extend([GeErdSensor(self, ErdCode.LAUNDRY_DRYER_SHEET_USAGE_CONFIGURATION, entity_category=EntityCategory.DIAGNOSTIC)])
        if self.has_erd_code(ErdCode.LAUNDRY_DRYER_SHEET_INVENTORY):
            dryer_entities.extend([GeErdSensor(self, ErdCode.LAUNDRY_DRYER_SHEET_INVENTORY, icon_override="mdi:tray-full", uom_override="sheets", entity_category=EntityCategory.DIAGNOSTIC)])
        if self.has_erd_code(ErdCode.LAUNDRY_DRYER_ECODRY_OPTION_SELECTION):
            dryer_entities.extend([GeErdSensor(self, ErdCode.LAUNDRY_DRYER_ECODRY_OPTION_SELECTION, entity_category=EntityCategory.DIAGNOSTIC)])

        return dryer_entities

    def get_dryer_passthrough_entities(self, existing_entities: List[Entity]):
        existing_erd_codes = {
            entity.erd_code
            for entity in existing_entities
            if hasattr(entity, "erd_code")
        }
        passthrough_entities = []

        for erd_code in sorted(self.appliance.known_properties, key=str):
            translated_erd_code = self.appliance.translate_erd_code(erd_code)
            if translated_erd_code in existing_erd_codes:
                continue
            if not self._is_dryer_passthrough_erd_code(translated_erd_code):
                continue

            passthrough_entities.append(
                GeErdSensor(
                    self,
                    translated_erd_code,
                    entity_category=EntityCategory.DIAGNOSTIC,
                )
            )
            existing_erd_codes.add(translated_erd_code)

        return passthrough_entities

    def _is_dryer_passthrough_erd_code(self, erd_code):
        erd_code_class = self.appliance.get_erd_code_class(erd_code)
        if erd_code_class == ErdCodeClass.LAUNDRY_DRYER_SENSOR:
            return True

        erd_name = erd_code.name if isinstance(erd_code, ErdCode) else str(erd_code)
        return erd_name.startswith("LAUNDRY_DRYER_")
