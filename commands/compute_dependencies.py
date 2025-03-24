#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import src
from collections import OrderedDict, defaultdict

parser = src.options.Options()
parser.add_option('p', 'products', 'list2', 'products',
    'Required: products to analyze dependencies for. This option accepts a comma separated list.')


def get_all_dependencies(config, product_name, dependencies=None, visited=None):
    '''Recursively get all dependencies for a product including dependencies of dependencies.
    
    :param config Config: The global configuration
    :param product_name str: The name of the product to analyze
    :param dependencies OrderedDict: Dictionary to store all dependencies
    :param visited set: Set of already visited products to avoid cycles
    :return: OrderedDict of all dependencies with their info
    '''
    if dependencies is None:
        dependencies = OrderedDict()
    if visited is None:
        visited = set()
        
    if product_name in visited:
        return dependencies
    
    try:
        product_info = src.product.get_product_config(config, product_name)
    except Exception as e:
        dependencies[product_name] = {"error": str(e)}
        return dependencies

    dependencies[product_name] = {
        "version": config.APPLICATION.products.get(product_name, "unknown"),
        "direct_deps": [],
        "optional_deps": []
    }

    if hasattr(product_info, 'depend'):
        dependencies[product_name]["direct_deps"] = list(product_info.depend)
        for dep in product_info.depend:
            get_all_dependencies(config, dep, dependencies, visited)

    if hasattr(product_info, 'opt_depend'):
        dependencies[product_name]["optional_deps"] = list(product_info.opt_depend)
        for dep in product_info.opt_depend:
            if dep in config.APPLICATION.products:
                get_all_dependencies(config, dep, dependencies, visited)

    visited.add(product_name)
    return dependencies

def get_flat_dependency_list(dependencies):
    '''Get a flat list of all unique dependencies.
    
    :param dependencies OrderedDict: Dictionary of all dependencies
    :return: List of tuples (product_name, version, is_optional)
    '''
    products = {}
    
    for product, info in dependencies.items():
        if "error" in info:
            continue
            
        if product not in products:
            products[product] = {
                "version": info["version"],
                "optional_only": True  # Start assuming it's optional
            }
            
    for info in dependencies.values():
        for dep in info.get("direct_deps", []):
            if dep in products:
                products[dep]["optional_only"] = False
                
    result = []
    for product, info in sorted(products.items()):
        result.append((
            product,
            info["version"],
            info["optional_only"]
        ))
    
    return result

def description():
    '''method that is called when salomeTools is called with --help option.
    
    :return: The text to display for the compute_dependency command description.
    :rtype: str
    '''
    return ("The compute_dependency command analyzes and displays all prerequisites "
            "required to install specified products.\n\n"
            "example:\nsat compute_dependency APPLICATION --products KERNEL,GUI,GEOM")

def run(args, runner, logger):
    '''method that is called when salomeTools is called with compute_dependency parameter.
    '''
    # Parse the options
    (options, args) = parser.parse_args(args)

    src.check_config_has_application(runner.cfg)

    if not options.products:
        logger.error("The --products option is required")
        return 1

    logger.write("Analyzing dependencies for products: %s\n" % 
                src.printcolors.printcLabel(", ".join(options.products)), 1)

    # Get all dependencies for each requested product
    all_dependencies = OrderedDict()
    for product in options.products:
        get_all_dependencies(runner.cfg, product, all_dependencies)

    flat_deps = get_flat_dependency_list(all_dependencies)
    
    logger.write("\nRequired products and dependencies:\n", 1)
    
    logger.write("\nMandatory:\n", 1)
    for product, version, is_optional in flat_deps:
        if not is_optional:
            logger.write(f"- {product} ({version})\n", 1)
    

    optional_count = sum(1 for product, _, is_opt in flat_deps if is_opt and product not in options.products)
    if optional_count > 0:
        logger.write("\nOptional:\n", 1)
        for product, version, is_optional in flat_deps:
            if is_optional and product not in options.products:
                logger.write(f"- {product} ({version})\n", 1)


    mandatory_count = sum(1 for _, _, is_opt in flat_deps if not is_opt)
    logger.write(f"\nSummary:\n", 1)
    logger.write(f"- Requested products: {len(options.products)}\n", 1)
    logger.write(f"- Total unique dependencies: {mandatory_count+optional_count}\n", 1)
    logger.write(f"  • Mandatory: {mandatory_count}\n", 1)
    logger.write(f"  • Optional: {optional_count}\n", 1)

    return 0 