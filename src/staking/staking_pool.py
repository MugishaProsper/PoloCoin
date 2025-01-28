from src.utils.Database import Database as db

class StakingPool:
    @staticmethod
    def add_stake(public_key, amount):
        """Add a stake for a node."""
        conn = db.get_connection()
        cursor = conn.cursor()

        # Check if the node already has a stake
        query_check = "SELECT total_stake FROM staking_pools WHERE public_key = %s;"
        cursor.execute(query_check, (public_key,))
        result = cursor.fetchone()

        if result:
            # Update the existing stake
            query_update = "UPDATE staking_pools SET total_stake = total_stake + %s WHERE public_key = %s;"
            cursor.execute(query_update, (amount, public_key))
        else:
            # Insert a new stake
            query_insert = "INSERT INTO staking_pools (public_key, total_stake) VALUES (%s, %s);"
            cursor.execute(query_insert, (public_key, amount))

        conn.commit()
        db.release_connection(conn)

    @staticmethod
    def remove_stake(public_key, amount):
        """Remove a stake from a node."""
        conn = db.get_connection()
        cursor = conn.cursor()

        # Check the current stake of the node
        query_check = "SELECT total_stake FROM staking_pools WHERE public_key = %s;"
        cursor.execute(query_check, (public_key,))
        result = cursor.fetchone()

        if result and result[0] >= amount:
            # Update the stake by subtracting the amount
            query_update = "UPDATE staking_pools SET total_stake = total_stake - %s WHERE public_key = %s;"
            cursor.execute(query_update, (amount, public_key))
        else:
            print("Not enough staked coins or node does not exist.")

        conn.commit()
        db.release_connection(conn)

    @staticmethod
    def get_stake(public_key):
        """Get the amount of staked coins for a node."""
        conn = db.get_connection()
        cursor = conn.cursor()

        query = "SELECT total_stake FROM staking_pools WHERE public_key = %s;"
        cursor.execute(query, (public_key,))
        result = cursor.fetchone()

        db.release_connection(conn)
        return result[0] if result else 0

    @staticmethod
    def select_validator():
        """Select a validator based on stake."""
        conn = db.get_connection()
        cursor = conn.cursor()

        # Fetch all stakes from the database
        query = "SELECT public_key, total_stake FROM staking_pools;"
        cursor.execute(query)
        stakes = cursor.fetchall()

        db.release_connection(conn)

        # Calculate the total staked amount
        total_staked = sum(stake[1] for stake in stakes)
        selected = None

        for public_key, stake in stakes:
            if selected is None or stake / total_staked > stakes[selected][1] / total_staked:
                selected = public_key

        return selected
