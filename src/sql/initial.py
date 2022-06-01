def check_record_table_exists(prefix):
    return """
    SELECT count(id) FROM {}_records
    """.format(
        prefix
    )


def check_record_predictions_exists(prefix):
    return """
    SELECT count(id) FROM {}_predictions 
    """.format(
        prefix
    )


def create_record_table(prefix):
    return """
 CREATE TABLE `{}_records` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `filepath` VARCHAR(45) NULL,
  `datetime` DATETIME NULL,
  `duration` DECIMAL(11, 6) NULL,
  `channels` TINYINT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC)
  );
    """.format(
        prefix
    )


def create_predictions_table(prefix):
    return """
CREATE TABLE `{}_predictions` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `record_id` INT NULL,
    `start_time` DECIMAL(11 , 6 ) NULL,
    `end_time` DECIMAL(11 , 6 ) NULL,
    `channel` INT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`record_id`)
        REFERENCES `{}_record` (`id`) ON DELETE CASCADE,
    UNIQUE INDEX `id_UNIQUE` (`id` ASC)
);
    """.format(
        prefix, prefix
    )
