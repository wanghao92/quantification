
-- 创建回测记录基本信息
create table IF NOT EXISTS `back_test_info`(
    `id` varchar(64),
    `strategy` varchar(64),
    `name`  datetime comment 'account name',
    `test_time` datetime comment '实际的测试时间',
    `start_time` datetime comment '回测范围起始时间',
    `end_time` datetime comment '回测范围截止时间',
    `init_money` float,
    `total_money` float,
    `remain` float,
    `profit` float,
    `market_value` float,
    `trade_cnt` int,
    `suc_cnt` int,
    `total_profit` int,
    `table_index` int,
    `description` longtext,
    primary key (`id`),
    index index_strategy (`strategy`),
    index index_test_time (`test_time`),
    index index_name (`name`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 创建回测记录实时账户信息
create table IF NOT EXISTS `real`(
    `id` varchar(64),
    `back_test_info_id` varchar(64),
    `date_time` datetime,
    `total_money` float,
    `remain` float,
    `market_value` float,
    `money_rate` float,
    `yield_rate` float,
    `profit` float,
    primary key (`id`),
    index index_back_info_id (`back_test_info_id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 回测记录单次交易
create table IF NOT EXISTS `deal_dot_0`(
    `id` varchar(64),
    `back_test_info_id` varchar(64),
    `stock_code` varchar(32),
    `stock_name` varchar(32),
    `stock_cnt` int,
    `deal_time` datetime,
    `price` float,
    `is_buy` boolean,
    primary key (`id`),
    index index_back_info_id (`back_test_info_id`),
    index index_is_buy (`is_buy`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 分钟/日行情
create table IF NOT EXISTS `zzmt`(
    `date_time` datetime comment '日期',
    `open` int comment '开盘 unit：1分',
    `close` int comment '收盘',
    `low` int comment '最低价',
    `high` int  comment '最高价',
    `volume` int comment '成交数 unit：1股',
    `money` int comment '成交金额 unit：1元',
    unique key index_date_time (`date_time`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;



-- 创建聚宽的股票基本信息表
create table IF NOT EXISTS `security_info`(
    `stock_code` varchar(64) ,
    `display_name` varchar(64) not null comment '中文名称',
    `simple_name` varchar(64) comment '缩写简称',
    `stock_type` varchar(8) not null comment '类型，stock(股票)，index(指数)，etf(ETF基金)，fja（分级A），fjb（分级B），fjm（分级母基金），mmf（场内交易的货币基金）open_fund（开放式基金）, bond_fund（债券基金）, stock_fund（股票型基金）, QDII_fund（QDII 基金）, money_market_fund（场外交易的货币基金）, mixture_fund（混合型基金）, options(期权)',
    `start_date` datetime comment '上市日期',
    `end_date` datetime comment '退市日期，如果没有退市则为2200-01-01',
    primary key (`stock_code`),
    index index_display_name (`display_name`),
    index index_simple_name (`simple_name`),
    index index_stock_type (`stock_type`),
    index index_start_date (`start_date`),
    index index_end_date (`end_date`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into security_info (`stock_code`, `display_name`, `simple_name`, `stock_type`, `start_date`, `end_date`)
values ('000001.XSHG', '上证指数', 'SZZS', 'index', '1991-07-15 00:00:00', '2200-01-01 00:00:00')