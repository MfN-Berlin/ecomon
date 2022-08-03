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
  `filepath` VARCHAR(320) NOT NULL,
  `filename` VARCHAR(64) NOT NULL,
  `record_datetime` DATETIME NULL,
  `duration` DECIMAL(11, 6) NOT NULL,
  `channels` TINYINT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `filepath_UNIQUE` (`id` ASC)
  );
    """.format(
        prefix
    )


def create_predictions_table(prefix, species):

    rows = " ".join(["  `{}` FLOAT NOT NULL,\n".format(s) for s in species])

    return """
CREATE TABLE `{p}_predictions` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `record_id` INT NULL,
    `start_time` DECIMAL(11 , 6 ) NULL,
    `end_time` DECIMAL(11 , 6 ) NULL,
    `channel` INT NULL,
 {r}
    PRIMARY KEY (`id`),
    FOREIGN KEY (`record_id`) 
        REFERENCES `{p}_records` (`id`) ON DELETE CASCADE,
    UNIQUE INDEX `id_UNIQUE` (`id` ASC)
);
    """.format(
        p=prefix, r=rows
    )
