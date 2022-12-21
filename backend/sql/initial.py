def create_jobs_table():
    return """
CREATE TABLE IF NOT EXISTS `jobs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `prefix` VARCHAR(64) NOT NULL,
  `status` ENUM('running', 'done', 'failed','pending') NOT NULL DEFAULT 'running',
  `type` ENUM('add_index', 'drop_index', 'create_sample','calc_bin_sizes','calc_predictions','calc_daily_histograms','calc_activation'),
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

