from discord import TextStyle, Interaction
from discord.ui import Modal, TextInput
from controllers.prediction_controller import PredictionController
from db import DB

from .prediction_embed import PredictionEmbed


class PredictionVoteModal(Modal, title="Cast your vote!"):
    def __init__(self, parent: PredictionEmbed, guess: int, point_balance: int):
        super().__init__(timeout=None)
        self.guess = guess
        self.parent = parent
        self.point_balance = point_balance
        self.channel_points = TextInput(
            label=f"Channel Points ({point_balance})",
            placeholder="50",
            style=TextStyle.short,
            min_length=1,
            required=True,
        )
        self.add_item(self.channel_points)

    async def on_submit(self, interaction: Interaction):
        try:
            channel_points = int(self.channel_points.value)
        except ValueError:
            await interaction.response.send_message(
                "Invalid point value", ephemeral=True
            )
            return

        await PredictionController.create_prediction_entry(
            channel_points, self.point_balance, self.guess, interaction
        )
        self.parent.update_fields()

        prediction_message_id = DB().get_prediction_message_id(interaction.guild_id)
        prediction_message = await interaction.channel.fetch_message(
            prediction_message_id
        )
        await prediction_message.edit(embed=self.parent)

        await interaction.response.send_message(
            f"Vote cast with {channel_points} points!", ephemeral=True
        )