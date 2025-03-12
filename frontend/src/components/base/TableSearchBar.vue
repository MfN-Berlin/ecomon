<script setup lang="ts">
type Headers = {
  title: string;
  key: string;
  align: "end" | "start" | "center";
  search: { operator: string; type: "number" | "text" };
};

type SearchDefineArgs = {
  key: string;
  operator: string;
  value: string | number;
  type: "text" | "number";
};
const { headers } = defineProps<{
  headers: Readonly<Headers[]>;
}>();

const emit = defineEmits<{
  (e: "update:key", value: SearchArgs): void;
  (e: "update:reset", value: { key: string }): void;
}>();

function transformValue(
  value: SearchDefineArgs["value"],
  type: SearchDefineArgs["type"],
  operator: SearchDefineArgs["operator"]
) {
  if (type === "text" && (operator === "_like" || operator === "_ilike")) {
    if (value === "" || value === null || value === undefined) {
      return undefined;
    }
    return `%${value}%`;
  }

  return value;
}
const handleSearch = ({ key, operator, value, type }: SearchDefineArgs) => {
  const transformedValue = transformValue(value, type, operator);
  if (transformedValue) {
    emit("update:key", {
      [key]: {
        [operator]: transformedValue
      }
    });
  } else {
    emit("update:reset", { key });
  }
};
</script>

<template>
  <tr>
    <td v-for="header in headers" :key="header.key" class="pa-2">
      <template v-if="header.search">
        <v-text-field
          v-if="header.search.type === 'text'"
          :key="header.key"
          :label="header.title"
          :type="header.search.type"
          density="compact"
          clearable
          @update:model-value="
            handleSearch({
              key: header.key,
              operator: header.search.operator,
              value: $event,
              type: header.search.type
            })
          "
        ></v-text-field>
        <v-number-input
          v-else
          :key="header.key + 'number'"
          :label="header.title"
          :type="header.search.type"
          density="compact"
          clearable
          :min="0"
          control-variant="hidden"
          @update:model-value="
            handleSearch({
              key: header.key,
              operator: header.search.operator,
              value: $event,
              type: header.search.type
            })
          "
        ></v-number-input>
      </template>
    </td>
  </tr>
</template>
