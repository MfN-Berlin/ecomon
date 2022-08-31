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
  `filename` VARCHAR(128) NOT NULL,
  `record_datetime` DATETIME NULL,
  `duration` DECIMAL(11, 6) NOT NULL,
  `channels` TINYINT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX record_datetime_index(`record_datetime` ASC),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `filepath_UNIQUE` (`filepath` ASC)
  );
    """.format(
        prefix
    )


def create_predictions_table(prefix, species):

    rows = " ".join(["  `{}` FLOAT NOT NULL,\n".format(s) for s in species])

    return """
CREATE TABLE `{p}_predictions` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `record_id` INT NOT NULL,
    `start_time` DECIMAL(11 , 6 ) NULL,
    `end_time` DECIMAL(11 , 6 ) NULL,
    `channel` VARCHAR(8) NOT NULL,
    {r}
    PRIMARY KEY (`id`),
    FOREIGN KEY (`record_id`) REFERENCES `{p}_records` (`id`) ON DELETE CASCADE,
    UNIQUE INDEX `id_UNIQUE` (`id` ASC),
    INDEX `channel_index` (`channel` ASC)

);
    """.format(
        p=prefix, r=rows
    )


def create_jobs_table():
    return """
CREATE TABLE IF NOT EXISTS `jobs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `prefix` VARCHAR(64) NOT NULL,
  `status` ENUM('running', 'done', 'failed','pending') NOT NULL DEFAULT 'running',
  `type` ENUM('add_index', 'drop_index', 'create_sample'),
  `metadata` JSON, 
  `progress` INT NOT NULL DEFAULT 0,
  `error` VARCHAR(256) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CHECK (JSON_VALID(`metadata`)),
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `updated_at_index` (`updated_at` DESC),
  INDEX `created_at_index` (`updated_at` DESC)
  );
    """
