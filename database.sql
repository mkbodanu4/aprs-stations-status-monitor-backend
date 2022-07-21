CREATE TABLE `call_signs`
(
    `call_sign_id` INT         NOT NULL AUTO_INCREMENT,
    `value`        VARCHAR(20) NOT NULL,
    `region_id`    INT         NOT NULL,
    PRIMARY KEY (`call_sign_id`),
    UNIQUE `call_sign_value` (`value`(20))
) ENGINE = InnoDB;

CREATE TABLE `regions`
(
    `region_id` INT         NOT NULL AUTO_INCREMENT,
    `title`     VARCHAR(30) NOT NULL,
    PRIMARY KEY (`region_id`),
    UNIQUE `title` (`title`(30))
) ENGINE = InnoDB;

CREATE TABLE `status`
(
    `status_id`       INT          NOT NULL AUTO_INCREMENT,
    `call_sign_id`    INT          NOT NULL,
    `date_last_heard` DATETIME     NOT NULL,
    `path`            VARCHAR(255) NOT NULL,
    `date_refreshed`  DATETIME     NOT NULL,
    PRIMARY KEY (`status_id`),
    UNIQUE `call_sing` (`call_sign_id`)
) ENGINE = InnoDB;